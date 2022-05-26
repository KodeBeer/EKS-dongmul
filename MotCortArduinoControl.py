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

        try:
            self.arduino = serial.Serial(thePort, theSpeed)          
            response = str(self.arduino.read().decode())

            startTime = time.time()
            while not 'i' in response:
                response = str(self.arduino.read().decode())                
                if (time.time() - startTime) > 5:
                    self.timeOut = True
                    break
            self.arduino.flush()  # make sure buffer is emptied. There may be noise on the line due to USB connection
        
        except Exception as e:
            print ("Something wrong in Arduino Setup: ")
            print(e) 

    def run(self, excitement, curiosity, finish, negVolume, posVolume, thisCommand):
        #self.port = port.value
        #self.speed = speed.value

        self.setUp()
        
        while finish.value == 0:
            if  self.arduino.inWaiting():
                self.logFile.write("from Arduino received: ")
                response = ""
                while self.arduino.inWaiting():
                    response += str(self.arduino.read().decode())  
                self.logFile.write(response)
                self.logFile.write("\n")
            self.excitement = excitement.value
            self.curiosity = curiosity.value
            self.excitement = '{: .2f}'.format(self.excitement * self.scaling)  # only 2 digits precision expected
            self.curiosity = '{: .2f}'.format(self.curiosity * self.scaling)
            
            if thisCommand.value == 1:
                freString = '1;'
                freString += str(negVolume.value)   
                freString += ';'
                freString += str(posVolume.value)
                self.arduino.write(freString.encode())            
                self.logFile.write("Calibration: " + str(freString + "\n" )) 
                thisCommand.value = -1


            if thisCommand.value == 0:                 
                freString = '0;'
                freString += str(self.excitement)   
                freString += ';'
                freString += str(self.curiosity)
                self.arduino.write(freString.encode())
                self.logFile.write("Values: " + str(freString + "\n" ))
                #print("Inside Arduino excitement, curiosity: " + str(excitement) + ", " + str(curiosity))
                thisCommand.value = -1
                
            if thisCommand.value == 2:
                freString = '2;'    
                self.arduino.write(freString.encode())      
                self.logFile.write("Reset issued with: ")
                self.logFile.write(freString)
                self.logFile.write("\n")               
                thisCommand.value = -1
                
            #print("Arduino Ready")
        self.arduino.close() 
        self.logFile.close()
  