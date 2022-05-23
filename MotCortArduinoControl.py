# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 19:36:50 2022

@author: Erwin
"""
import serial 
import time
from time import sleep

class Arduino():
    def __init__(self, port, speed):
        self.port = port
        self.speed = speed
        self.timeOut = False

    def setUp(self):          
        thePort = "COM" + str(self.port)
        theSpeed = str(self.speed)
        self.scaling = 1.0
        self.excitement = 0.5
        self.curiosity = 0.5
        self.logFile = open("Arduinolog.txt", "w")
        self.logFile.write("setUP Arduino \n")

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
            self.arduino.flush()  # make sure buffer is emptied. There may be noise on the line due to USB connection
            self.logFile.write("Maybe init, timeout is: " + str(self.timeOut) + "\n")
            freString = '0;'
            freString += str(0.5)   
            freString += ';'
            freString += str(0.5)

            self.arduino.write(freString.encode()) # to start syncing
            self.logFile.write("sent data in INIT is: " + str(freString))

        
        except Exception as e:
            print ("Something wrong in Arduino Setup: ")
            print(e) 

    def run(self, excitement, curiosity, finish, negVolume, posVolume):
        #self.port = port.value
        #self.speed = speed.value

        self.setUp()
        
        while  finish.value == 0:
            if self.arduino.inWaiting():
                response = str(self.arduino.read().decode())           
            self.excitement = excitement.value
            self.curiosity = curiosity.value
            self.excitement = '{: .2f}'.format(self.excitement * self.scaling)  # only 2 digits precision expected
            self.curiosity = '{: .2f}'.format(self.curiosity * self.scaling)
            freString = '1;'
            freString += str(negVolume.value)   
            freString += ';'
            freString += str(posVolume.value)
            self.arduino.write(freString.encode())            
            self.logFile.write("Calibration: " + str(freString + "\n" ))                      
            freString = '0;'
            freString += str(self.excitement)   
            freString += ','
            freString += str(self.curiosity)
            self.arduino.write(freString.encode())
            self.logFile.write("Values: " + str(freString + "\n" ))
            #print("Inside Arduino excitement, curiosity: " + str(excitement) + ", " + str(curiosity))
            sleep(0.1)
            #print("Arduino Ready")
        self.arduino.close() 
        self.logFile.close()
  