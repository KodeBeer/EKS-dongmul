# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 19:36:50 2022

@author: Erwin
"""

import serial
from time import sleep

class arduinoController():
    def __init__(self, port, speed, exciteIdx = 0, curiosityIdx = 1):
        self.port = port
        self.speed = speed
        self.scaling = 1.0
        self.exciteIdx = exciteIdx
        self.curiosityIx = curiosityIdx
        self.arduinoStarted = False
        self.paused = False
        print ("Init usb handler with port: " + self.port + " speed: " + str(self.speed) )
        try:
            self.arduino = serial.Serial(self.port, self.speed)          
            response = str(self.arduino.read().decode())
            """
            TODO: make sure system does not hang up, set time out
            """
            while not 'i' in response:
                response = str(self.arduino.read().decode())
            print("Connection to " + self.port + " established succesfully!\n")
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

    def checkArduinoStarted(self):
        return self.arduinoStarted
            
    def run(self, finish, moodData, dataSent):
        if self.arduinoStarted:  # This is after communication with Arduino was succesfully started
            while not finish.is_set():
                if not self.paused:
                    response = str(self.arduino.read().decode())
                    if ('r' in response):  # r is message sent by Arduino to indicate ready for next command
                        theMood = moodData.get()
                        excitement = theMood[self.exciteIdx]
                        curiosity = theMood[self.curiosityIx]
                        excitement = '{: .2f}'.format(excitement * self.scaling)  # only 2 digits precision expected
                        curiosity = '{: .2f}'.format(curiosity * self.scaling)
                        freString = str(excitement)   
                        freString += ','
                        freString += str(curiosity)
                        freString += '\n' 
                        self.arduino.write(freString.encode())
                        print("Inside Arduino excitement, curiosity: " + str(excitement) + ", " + str(curiosity))
                        dataSent.set()
                        sleep(0.2)
                        #print("Arduino Ready")
            self.arduino.close()
            
    def setUsbPort(self, port):
        self.port = port
        print ("Updated port to: " + self.port)
        
    def setSpeed(self, speed):
        self.speed = speed
        
        
    def setScaling(self, scale):      
        self.scaling = scale
        
    def setPaused(self, paused):
        self.paused = paused
        print ("Arduino Paused is: " + str(self.paused))
        
        