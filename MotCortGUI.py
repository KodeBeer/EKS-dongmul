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
#from time import sleep    
        
class mprocExample(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.num = mp.Value('d', 0.0)
        #self.arr = mp.Array('i', range(10)) 
        self.excitement = mp.Value('d', 0.5)
        self.curiosity = mp.Value('d', 0.5)
        self.ArduinoRunning = False
        self.theArduino = Arduino()
        self.theEEG = EEG()
        self.finish = mp.Value('i', 0)
        self.initGui()
        
    def initGui(self):
        self.title("that title broh")
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
                
        self.update()   

    def stopRun(self) :
        self.finish.value = 1
        print ("finished it")

    def run(self, *args): 
        while self.finish.value == 0:
            self.update()  
            
        self.p.join()
        print(self.excitement.value)
        print(self.curiosity.value)
        self.destroy()
        
    def startArduino(self):
        if not self.ArduinoRunning:
            print ("Start de Arduino")
            comPort = int(self.portEntry.get())
            print (comPort)
            port = mp.Value( 'i', comPort)  
            speed = mp.Value('i', 9600) 
            self.ArduinoRunning = True
            self.p = mp.Process(target=self.theArduino.run, args=(self.excitement, self.curiosity, self.finish,  port, speed))
            self.p.start()    


if __name__ == '__main__':
    app = mprocExample()
    app.run()