# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 19:36:50 2022

@author: Erwin
"""
import serial 
import time
from time import sleep

class Arduino():
    def __init__(self):
        self.ardsuccess = 314.15
        
        
    def setUp(self):          
        thePort = "COM" + str(self.port)
        theSpeed = str(self.speed)

        try:
            self.arduino = serial.Serial(thePort, theSpeed)          
            response = str(self.arduino.read().decode())
            """
            TODO: make sure system does not hang up, set time out
            """
            startTime = time.time()
            while not 'i' in response:
                response = str(self.arduino.read().decode())                
                if (time.time() - startTime) > 5:
                    self.timeOut = True
                    break
                
            #print("Connection to " + str(self.port) + " established succesfully!\n")
            self.ardsuccess = 1.0
            self.arduino.flush()  # make sure buffer is emptied. There may be noise on the line due to USB connection
            freString = str(0.0)   
            freString += ','
            freString += str(0.0)
            freString += '\n' 
            self.arduino.write(freString.encode()) # to start syncing
            self.arduinoStarted = True
        
        except Exception as e:
            print ("Something wrong in Arduino Setup: ")
            print(e) 
            self.ardsuccess = -11.1

    def run(self, excitement, curiosity, port, speed):
        self.port = port.value
        self.speed = speed.value

        self.setUp()
        excitement.value = self.ardsuccess
        curiosity.value = 9.11
        
  