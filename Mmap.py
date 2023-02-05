
import cv2 as cv
import numpy as np
import pyautogui as pg
import random


class Map:
    OUT_OF_BOUNDS = -6
    MARKED = -3
    UNPROBED = -5
    BOOM = -1



    def __init__(self):
        self.mapfail = False
        self.row = 0
        self.cols = 0
        self.mmm = 0

        self.mine_map = None #-1 if cell(x,y) has a mine, or n for constraint factor

        self.mark_map = None #true whenn cell(x,y) is marked
        #relation: mark_map[x][y] == true implies unprobed_map[x][y] == true
        self.unprobed_map = None #true when cell(x,y) is not probed

    def MineMap(self,numMines):
                

        

        screenshot = pg.screenshot('screenshot.png')


        squareLocs = findClickPositions('blank.png','screenshot.png',0.75)
        spaces = []
        temp = 1
        for square in squareLocs:
            if square[1] != temp:
                self.row += 1
                temp = square[1]
            spaces.append('-')
        self.cols = int( len(squareLocs) / self.row )

        
        self.mine_map = [[-1 for j in range(self.cols)]for i in range(self.row)]
        self.mark_map = [[False for j in range(self.cols)]for i in range(self.row)]
        self.unprobed_map = [[True for j in range(self.cols)]for i in range(self.row)]
        l=[[[0,0] for j in range(self.cols)]for i in range(self.row)]
        self.coord_map = l


        for i in range(self.row):
            for j in range(self.cols):
                self.coord_map[i][j] = squareLocs[j+(self.cols*i)]
                self.unprobed_map[i][j] = True
                self.mark_map[i][j] = False
                self.mine_map[i][j] = self.UNPROBED
        self.mmm = numMines
        return

    def display(self):
        for i in range(self.row):
            for j in range(self.cols):
                if j < self.cols-1:
                    ending = ' '
                else:
                    ending = '\n'

                if self.mine_map[i][j] == self.UNPROBED:
                    print("- ", end = ending)
                else:
                    print(self.mine_map[i][j], end = ending)

    
    def columns(self):
        return self.cols 
    
    def rows(self):
        return self.row 
    
    def mines_minus_marks(self):
        return self.mmm 

    def mark(self,x,y):

        if x < 0 or x >= self.row or y < 0 or y >= self.cols:
            return Map.OUT_OF_BOUNDS
        elif self.mark_map[x][y] == True:
            return Map.MARKED
        elif self.unprobed_map[x][y]:
            pg.click(self.coord_map[x][y],button='right')
            self.mmm -= 1
            self.mark_map[x][y] = True
            return Map.MARKED
        else:
            return self.mine_map[x][y]

        #ADD A RIGHT CLICK
    def unmark(self,x,y):
        if x < 0 or x >= self.row or y < 0 or y >= self.cols:
            return Map.OUT_OF_BOUNDS
        elif self.mark_map[x][y]:
            pg.click(self.coord_map[x][y],button='right')
            self.mmm += 1
            self.mark_map[x][y] = False
            return Map.UNPROBED
        elif self.unprobed_map[x][y]:
            return Map.UNPROBED
        else:
            return self.mine_map[x][y]

    def look(self,x,y):
        if x < 0 or x >= self.row or y < 0 or y >= self.cols:
            return Map.OUT_OF_BOUNDS
        elif self.mark_map[x][y]:
            return Map.MARKED
        elif self.unprobed_map[x][y]:
            return Map.UNPROBED
        else:
            return self.mine_map[x][y]

    def probe(self,x,y):
        if x < 0 or x >= self.row or y < 0 or y >= self.cols:
            return Map.OUT_OF_BOUNDS
        elif self.mark_map[x][y] == True:
            return Map.MARKED
                
        pg.click(self.coord_map[x][y])

        self.mine_map, self.unprobed_map = updateSpaces('0.png',0,self.mine_map,self.unprobed_map,self.coord_map)
        self.mine_map, self.unprobed_map = updateSpaces('1.png',1,self.mine_map,self.unprobed_map,self.coord_map)
        self.mine_map, self.unprobed_map = updateSpaces('2.png',2,self.mine_map,self.unprobed_map,self.coord_map)
        self.mine_map, self.unprobed_map = updateSpaces('3.png',3,self.mine_map,self.unprobed_map,self.coord_map)
        self.mine_map, self.unprobed_map = updateSpaces('4.png',4,self.mine_map,self.unprobed_map,self.coord_map)
        self.mine_map, self.unprobed_map = updateSpaces('5.png',5,self.mine_map,self.unprobed_map,self.coord_map)
        self.mine_map, self.unprobed_map = updateSpaces('6.png',6,self.mine_map,self.unprobed_map,self.coord_map)

        fail = checkBombs()
        if fail == 1:
            self.mapfail = True
        return self.mine_map[x][y]

    def done(self):
        return self.mapfail
    
def findClickPositions(needle_img_path, haystack_img_path, threshold, debug_mode=None):
    
    haystack_img = cv.imread(haystack_img_path, cv.IMREAD_UNCHANGED)
    needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
    # Save the dimensions of the needle image
    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]

    # There are 6 methods to choose from:
    # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack_img, needle_img, method)

    # Get the all the positions from the match result that exceed our threshold
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
    # locations by using groupRectangles().
    # First we need to create the list of [x, y, w, h] rectangles
    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        # Add every box to the list twice in order to retain single (non-overlapping) boxes
        rectangles.append(rect)
        rectangles.append(rect)
    # Apply group rectangles.
    # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
    # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
    # in the result. I've set eps to 0.5, which is:
    # "Relative difference between sides of the rectangles to merge them into a group."
    rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

    points = []
    if len(rectangles):

        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:

            # Determine the center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            # Save the points
            points.append((center_x, center_y))

            if debug_mode == 'rectangles':
                # Determine the box position
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                # Draw the box
                cv.rectangle(haystack_img, top_left, bottom_right, color=line_color, 
                             lineType=line_type, thickness=2)
            elif debug_mode == 'points':
                # Draw the center point
                cv.drawMarker(haystack_img, (center_x, center_y), 
                              color=marker_color, markerType=marker_type, 
                              markerSize=40, thickness=2)

        if debug_mode:
            cv.imshow('Matches', haystack_img)
            cv.waitKey()
            #cv.imwrite('result.jpg', haystack_img)

    return points

def updateSpaces(number_image_path,name,spaces,unprobed,base_coords):
    screenshot = pg.screenshot('screenshot.png')
    nums = findClickPositions(number_image_path,'screenshot.png',0.75)
    i = 0
    for i in range(len(base_coords)):
        for j in range(len(base_coords[i])):
                for num in nums:
                    if ((num[0] < (base_coords[i][j][0] + 5)) and (num[0] > (base_coords[i][j][0] - 5)) and (num[1] < (base_coords[i][j][1] + 5)) and (num[1] > (base_coords[i][j][1] - 5))):
                        spaces[i][j] = name
                        unprobed[i][j] = False
                                
                    
            

    return spaces, unprobed
def checkBombs():
    screenshot = pg.screenshot('screenshot.png')
    nums = findClickPositions('bomb.png','screenshot.png',0.75)

    if(nums):
        return 1
    else:
        return 0

