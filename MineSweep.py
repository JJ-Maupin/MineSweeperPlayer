
import cv2 as cv
import numpy as np
import pyautogui as pg
import random


from Mmap import Map
from MBPos import BoardPosition

class CSPStrategy:
    
    VERBOSE = True
    SOLVE_THRESHOLD = 20

    def __init__(self,map):
        

        self.map = map

        self.constraints = []
        self.nconstraints = 0

    def play(self,map):
        BoardPosition.CreateBoard(self.map)
        notProbed = 0
        while not self.map.done():
                
            self.constraints = []
            self.nconstraints = 0
            #initialize constraints;
            for x in range(self.map.rows()):
                for y in range(self.map.columns()):
                    self.addConstraint(BoardPosition.board[x][y].newConstraint())

            probed = self.simplifyConstraints()
            if(self.map.done()):
                break
            elif not probed:
                notProbed += 1
            elif probed:
                notProbed = 0
            
            if notProbed >= 3:
                positions = BoardPosition.enumerateCorners()
                type = "corner"
                if positions == None:
                    positions = BoardPosition.enumerateEdges()
                    type = "edge"
                if positions == None:
                    positions = BoardPosition.enumerateMaxBoundary()
                    type = "boundary"
                if positions == None:
                    positions = BoardPosition.enumerateUnknown()
                    type = "far"
                if positions == None:
                    print("NOTHING? NO UNKNOWN OR BOUNDARY!?")
                    positions = BoardPosition.enumerateMaxBoundary()
                

                i = random.randint(0,len(positions)-1)
                s = positions[i].probe(self.map)
                notProbed = 0
        



    def addConstraint(self,c):
        if c == None:
            return
        self.constraints.append(c)
        self.nconstraints += 1



    def simplifyConstraints(self):
        done = False
        probed = False
        while not done:
            done = True
            



            for i in range(self.nconstraints):
                #Will remove any constraints that are all mines or not mines, returns a list of constraints that is either empty or what is left
                probed = self.constraints[i].updateAndRemoveKnownVariables(self.map)


            if not done:
                continue
            for i in range(self.nconstraints):
                #If empty, eliminate
                while (i < self.nconstraints):
                    if(self.constraints[i].isEmpty()):
                        self.constraints.pop(i)
                        self.nconstraints -= 1
                    else:
                        break
                #Simplify the remaining constraints
                if i < self.nconstraints:
                    for j in range(i+1,self.nconstraints):
                        if self.constraints[i].simplify(self.constraints[j]):
                            done = False

        return probed










print("Warning, Currently this program is in development, should you need to forcibly end the program, move your mouse to the corner of your screen.")
numMines = int(input("How Many Mines Are We playing with: "))

map = Map()
map.MineMap(numMines)

strat = CSPStrategy(map)
strat.play(map)

