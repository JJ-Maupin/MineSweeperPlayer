
import cv2 as cv
import numpy as np
import pyautogui as pg
import random


from Mmap import Map



#Represents a single minesweeper board position. 
class BoardPosition:

    #Values:
    UNKNOWN=-5
    CONSTRAINED=-4
    MARKED=-3
    CLEAR=0 #or greater 


    #Counts: 
    unknown=None
    constrained=None
    mine=None
    clear=None





    #Construct the board and all poisition instances for given map
    def CreateBoard(map):
        BoardPosition.unknown=0
        BoardPosition.constrained=0
        BoardPosition.mine=0
        BoardPosition.clear=0

        BoardPosition.board = [[None for j in range(map.columns())]for i in range(map.rows())]
        for i in range(map.rows()):
            for j in range(map.columns()):
                BoardPosition.board[i][j] = BoardPosition(i,j)
        headstart=False
        for i in range(map.rows()):
            for j in range(map.columns()):
                s = map.look(i,j)
                if s == Map.MARKED:
                    BoardPosition.board[i][j].setState(BoardPosition.MARKED)
                elif s >= 0:
                    BoardPosition.board[i][j].setState(s)
                    headstart = True


        return headstart


    def nonConstrainedCount():
        return BoardPosition.unknown
           




           #Enumerate all unknown positions with a particular boundary level
    def enumerateBoundary(level):
        result = []
        count = 0
        for i in range(len(BoardPosition.board)):
            for j in range(len(BoardPosition.board[i])):
                if BoardPosition.board[i][j].state == BoardPosition.UNKNOWN and BoardPosition.board[i][j].boundary_level == level:
                    result.append(BoardPosition.board[i][j]) #
                    count += 1

        if count == 0:
            return None
        
        if count < len(result):
            newresult = []
            for i in range(count):
                newresult.append(result[i]) 
            result = newresult
        return result






    def enumerateMaxBoundary():
        max = 0

        for i in range(len(BoardPosition.board)):
            for j in range(len(BoardPosition.board[i])):
                if BoardPosition.board[i][j].state == BoardPosition.UNKNOWN and BoardPosition.board[i][j].boundary_level > max:
                    max = BoardPosition.board[i][j].boundary_level
        if max == 0:
            return None
        result = BoardPosition.enumerateBoundary(max)
        return result





    def enumerateUnknown():
        if BoardPosition.unknown == 0:
            return None
        result = []
        count = 0

        for i in range(len(BoardPosition.board)):
            for j in range(len(BoardPosition.board[i])):
                if BoardPosition.board[i][j].state == BoardPosition.UNKNOWN:
                    result.append(BoardPosition.board[i][j])
        if count != BoardPosition.unknown:
            print("OOPS")
        return result




    def enumerateEdges():
        v = []
        for i in range(len(BoardPosition.board)):
            if BoardPosition.board[i][0].state < BoardPosition.CONSTRAINED:
                v.append(BoardPosition.board[i][0])
            if BoardPosition.board[i][len(BoardPosition.board[i])-1].state < BoardPosition.CONSTRAINED:
                v.append(BoardPosition.board[i][len(BoardPosition.board[i])-1])
        
        for i in range(len(BoardPosition.board[0])):
            if BoardPosition.board[0][i].state < BoardPosition.CONSTRAINED:
                v.append(BoardPosition.board[0][i])
            if BoardPosition.board[len(BoardPosition.board)-1][0].state < BoardPosition.CONSTRAINED:
                v.append(BoardPosition.board[len(BoardPosition.board)-1][i])
        if len(v) == 0:
            return None

        return v


    def enumerateCorners():
        result = [None] * 4
        count = 0
        
        if BoardPosition.board[0][0].state < BoardPosition.CONSTRAINED:#Top Left
            result[count] = BoardPosition.board[0][0]
            count += 1
        if BoardPosition.board[len(BoardPosition.board)-1][0].state < BoardPosition.CONSTRAINED: #Bottom Left
            result[count] = BoardPosition.board[len(BoardPosition.board)-1][0] 
            count += 1
        if BoardPosition.board[0][len(BoardPosition.board[0])-1].state < BoardPosition.CONSTRAINED: #Top Right
            result[count] = BoardPosition.board[0][len(BoardPosition.board[0])-1]
            count += 1
        if BoardPosition.board[len(BoardPosition.board)-1][len(BoardPosition.board[0])-1].state < BoardPosition.CONSTRAINED: #BottomRight
            result[count] = BoardPosition.board[len(BoardPosition.board)-1][len(BoardPosition.board[0])-1]
            count += 1

        if count == 0:
            return None 
        if count == 4:
            return result

        newresult = [None] * count
        for i in range(count):
            newresult[i] = result[i]
        return newresult



    def __init__(self,x,y):
        
        
        self.testAssignment=None
        
        self.state = BoardPosition.UNKNOWN
        self.boundary_level = 0 
        BoardPosition.unknown += 1

        self.x = x
        self.y = y

        if x != 0:
            self.nx1 = x-1
        else:
            self.nx1 = x
        if x != len(BoardPosition.board)-1:
            self.nx2 = x+2
        else:
            self.nx2 = x+1
            
        if y != 0:
            self.ny1 = y-1
        else:
            self.ny1 = y
        if y != len(BoardPosition.board[0])-1:
            self.ny2 = y+2
        else:
            self.ny2 = y+1

    def toString(self):

        if self.state == BoardPosition.UNKNOWN:
            c = 'U'
        elif self.state == BoardPosition.CONSTRAINED:
                c = 'C'
        elif self.state == BoardPosition.MARKED:
                c = 'M'
        else: 
            c = ' '
        return (c + str(self.x) + ',' + str(self.y))


    def newConstraint(self):
        if self.state < 0:
            return None
        
        from Mconstraints import Constraint
        
        c = Constraint()
        constant = self.state

        for i in range(self.nx1,self.nx2,1):
            for j in range(self.ny1,self.ny2,1):
                if self.board[i][j].state < 0:
                    if self.board[i][j].state == BoardPosition.MARKED:
                        constant -= 1
                    else:
                        c.add(self.board[i][j])
                        self.board[i][j].setState(BoardPosition.CONSTRAINED)
        c.setConstant(constant)

        return c


    def mark(self,map):
        map.mark(self.x,self.y)
        self.setState(BoardPosition.MARKED)

    def probe(self,map):
        result = map.probe(self.x,self.y)
        BoardPosition.board[self.x][self.y].setState(result)
        for i in range(map.rows()):
            for j in range(map.columns()):
                s = map.look(i,j)
                if s == Map.MARKED:
                    BoardPosition.board[i][j].setState(BoardPosition.MARKED)
                elif s >= 0:
                    BoardPosition.board[i][j].setState(s)
        return BoardPosition.board[self.x][self.y].state

    def getState(self):
        return self.state

    def setState(self,state):
        if self.state == state:
            return

        if self.state == BoardPosition.UNKNOWN:
            BoardPosition.unknown -= 1
        elif self.state == BoardPosition.CONSTRAINED:
            BoardPosition.constrained -= 1
        elif self.state == BoardPosition.MARKED:
            BoardPosition.mine -= 1
        else:
            BoardPosition.clear -= 1

        self.state = state

        if state == BoardPosition.UNKNOWN:
            BoardPosition.unknown += 1
        elif state == BoardPosition.CONSTRAINED:
            BoardPosition.constrained += 1
            self.boundary_level = 0

            for i in range(self.nx1,self.nx2,1):
                for j in range(self.ny1,self.ny2,1):
                    if BoardPosition.board[i][j].state == BoardPosition.UNKNOWN:
                        BoardPosition.board[i][j].boundary_level += 1
        elif state == BoardPosition.MARKED:
            BoardPosition.mine += 1
            self.boundary_level = 0

            for i in range(self.nx1,self.nx2,1):
                for j in range(self.ny1,self.ny2,1):
                    if BoardPosition.board[i][j].state == BoardPosition.UNKNOWN:
                        BoardPosition.board[i][j].boundary_level -= 1
        else:
            self.boundary_level = 0

    



