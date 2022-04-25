# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 20:42:48 2022

@author: Erwin
"""

class arduinoController():
    def __init__ (self, baud, port):
        self.arduinoStarted = True
        
        
    def run(self, finish, theArray):
        self.arduinoStarted = True   
        finish.value = True
        theArray[0] = 3
        
    def checkArduinoStarted(self):
        return self.arduinoStarted