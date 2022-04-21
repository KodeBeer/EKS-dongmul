# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 20:30:03 2022
Adapted 14 MArch

@author: Erwin
"""
import tkinter as tk
#from tkinter import ttk

import multiprocessing as mp
from MotCortArduinoControl import Arduino 
from MotCortEEGControl import EEG
from time import sleep  
import time  
        
class mprocExample(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.num = mp.Value('d', 0.0)
        #self.arr = mp.Array('i', range(10)) 
        self.excitement = mp.Value('d', 0.0)
        self.curiosity = mp.Value('d', 0.5)
        self.eegStatus = mp.Value('i', 0)
        self.ArduinoRunning = False
        self.eegRunning = False
        self.finish = mp.Value('i', 0)
        self.initGui()
        
    def initGui(self):
        self.title("Motor Cortex Control")
        self.geometry("800x600")
        self.resizable(width = True, height = True)
        self.attributes("-topmost", True) 
        self.stopButton = tk.Button(self, text="Stop", command = self.stopRun)
        self.stopButton.grid(column = 5, row = 1, sticky = 'we')        
        """
            Arduino GUI settings
        """
        self.startArduinoButton = tk.Button(self, text="Start Arduino", command = self.startArduino)
        self.startArduinoButton.grid(column = 0, row = 1, sticky = 'we') 
        self.portLabel =tk.Label(self, text = "Port nbr")
        self.portLabel.grid(column = 1, row = 1, sticky ='nwe')
        self.portEntry =  tk.Entry(self)
        self.portEntry.grid(column = 2, row = 1, sticky ='nwe')
        self.portEntry.insert( -1, "3")
        self.speedLabel =tk.Label(self, text = "Serial Speed")
        self.speedLabel.grid(column = 3, row = 1, sticky ='nwe')
        self.speedEntry =  tk.Entry(self)
        self.speedEntry.grid(column = 4, row = 1, sticky ='nwe')
        self.speedEntry.insert(-1, "9600")
        
        """ 
        EEG settings
        """
        self.startEEGButton = tk.Button(self, text="Start EEG", command = self.startEEG)
        self.startEEGButton.grid(column = 0, row = 2, sticky = 'we')        
                
        self.update()   

    def stopRun(self) :
        self.finish.value = 1
        print ("finished it")

    def run(self, *args): 
        lastTime = time.time()
        while self.finish.value == 0:  
            if time.time() - lastTime > 1 :
                print ("Curiosity" + str(self.curiosity.value))
                print ("Excitement" + str(self.excitement.value))
                lastTime = time.time()
            self.update()  
        
        if self.finish.value == 2:
            print ("eeg Status error: " + self.eegStatus.value)
            
        if self.finish.value == 3:
            print ("EEG never started")
        
        if self.ArduinoRunning:
            self.ArduinoRunning = False
            self.ardProc.join()
        if self.eegRunning:
            self.eegRunning = False
            self.eegProc.join()
        print(self.excitement.value)
        print(self.curiosity.value)
        self.destroy()
 
    def startEEG(self):  
        if not self.eegRunning:
            self.theEEG = EEG()
            self.eegProc = mp.Process(target=self.theEEG.run, args=(self.excitement, self.curiosity, self.finish, self.eegStatus))
            self.eegProc.start() 
            self.eegRunning = True
        
 
    def startArduino(self):
        if not self.ArduinoRunning:
            comPort = int(self.portEntry.get())
            speed = int(self.speedEntry.get())
            self.theArduino = Arduino(comPort, speed)
            self.ArduinoRunning = True
            self.ardProc = mp.Process(target=self.theArduino.run, args=(self.excitement, self.curiosity, self.finish))
            self.ardProc.start()    


if __name__ == '__main__':
    app = mprocExample()
    app.run()