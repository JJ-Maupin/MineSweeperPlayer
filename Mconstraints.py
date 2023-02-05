
import cv2 as cv
import numpy as np
import pyautogui as pg
import random

from Mmap import Map

from MBPos import BoardPosition






class Constraint:

    def __init__(self,constant = 0):
        
        self.nvariables = 0
        self.variables = []
        self.constant = constant

    def toString(self):
        if self.nvariables <= 0:
            return "[EMPTY CONSTRAINT]"
        s = str(self.constant) + "="
        s.append(self.variables[0])

        for i in range(self.nvariables):
            s.append("+"+self.variables[i])
        return s

    def add(self,c):
        
        self.variables.append(c)
        self.nvariables += 1
    
    def getVariables(self):
        return self.variables

    def getVariableCount(self):
        return self.nvariables

    def setConstant(self,c):
        self.constant = c
    
    def getConstant(self):
        if self.constant < 0:
            print("BAD CONSTANT")
        return self.constant

    def isEmpty(self):
        return (self.nvariables <= 0)




    def isSatisfied(self):
        if self.current_constant > self.constant:
            return False
        elif self.unassigned > 0:
            return True
        return (self.current_constant == self.constant)



    def updateAndRemoveKnownVariables(self,map):
        
        for i in range(self.nvariables - 1,-1,-1):
            s = self.variables[i].getState()
            #if the variable is already probed, pop
            if s >= 0:
                self.nvariables = self.nvariables - 1
                self.variables.pop(i)
            #if the variable is already marked, pop
            elif s == -3:
                self.nvariables = self.nvariables - 1
                self.variables.pop(i)
                self.constant = self.constant - 1

        #if nvariables is now empty, return None        
        if self.nvariables <= 0:
            return None


        result = False
        #If the constant is 0, then all are clear, probe them all.
        if self.constant == 0:
            for i in range(self.nvariables):
                self.variables[i].probe(map)
                result = True
        #If the constant is equal to  the number of variables, then they are all mines, mark them all
        elif self.constant == self.nvariables:
            for i in range(self.nvariables):              
                self.variables[i].mark(map)
                
        else:
            return None
        
        self.nvariables = 0
        self.constant = 0
        return result


    def simplify(self,other):
        if self.nvariables < other.nvariables:
            return other.simplify(self)

        for i in range(other.nvariables):
            for j in range(self.nvariables):
                if self.variables[j] == (other.variables[i]):
                    break
                elif j >= self.nvariables -1:
                    return False
        
        for i in range(other.nvariables):
            for j in range(self.nvariables):
                if self.variables[j] == other.variables[i]:
                    self.nvariables -= 1
                    self.variables.pop(j)
                    break 

        self.constant -= other.constant
        return True 

    def coupledWith(self,other):
        for i in range(other.nvariables):
            for j in range(self.nvariables):
                if self.variables[j] == other.variables[i]:
                    return True
        return False




