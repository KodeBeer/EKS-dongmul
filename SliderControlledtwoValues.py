# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 16:32:20 2021

@author: Erwin
"""


import tkinter as tk
from tkinter import ttk
#from tkinter import IntVar

import serial
import time


class AlphaSource(tk.Tk):
   
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initTheGui() 
        self.arduinoStarted = False
        self.measuredone = True
        self.measureLoop()
        self.arduino = serial.Serial()
        self.arduinoReady = False

        self.excitement = self.excitementcurrent_value.get()
        self.excitement = round(self.excitement, 4)
        self.curiosity = self.curiositycurrent_value.get()
        self.curiosity = round(self.curiosity, 4)         
            
    def measureLoop(self):    
        self.excitement = self.excitementcurrent_value.get()
        self.excitement = round(self.excitement, 4)
        self.curiosity = self.curiositycurrent_value.get()
        self.curiosity = round(self.curiosity, 4) 
        
        if self.arduinoStarted:  # This is after communication with Arduino was succesfully started
            response = str(self.arduino.read().decode())

            if ('r' in response):  # r is message sent by Arduino to indicate ready for next command
                self.response_label.config(text = "Ready")
                self.sendEEGButton["state"] = tk.NORMAL 
                self.update()
                #print("Arduino Ready")
              
            if ('e' in response): # Arduino indicates it is busy executing the command
                self.response_label.config(text = "Executing")  
                self.sendEEGButton["state"] = tk.DISABLED  
                self.update()
                #print ("Arduino Busy")
            self.update()  # Make sure GUI is ready and up to date    
       
        self.after(50, self.measureLoop) # restart measure loop after 50 msec

        
    def stop(self):
        self.arduino.close()
        self.destroy()
        
    def initTheGui(self):
        self.title("Excitement Curiosity simulator")
        self.geometry("600x400")
        self.resizable(width = True, height = True)
        # slider current value
        self.excitementcurrent_value = tk.DoubleVar()
        self.curiositycurrent_value = tk.DoubleVar()   
        
        excitementSlider = ttk.Scale(self,from_= 1 ,to= 0, orient='vertical', command=self. excitementSlider_changed, 
                                 variable=self.excitementcurrent_value)
        excitementSlider.grid(column=0,row=0,sticky='we')
        excitementcurrent_value_label = ttk.Label(self, text='Excitement:')       
        excitementcurrent_value_label.grid(row=1, column = 0,  sticky='n', ipadx=10, ipady=10)
        self.excitementvalue_label = ttk.Label(self, text=self.excitementget_current_value())
        self.excitementvalue_label.grid(row=4, column = 0,  sticky='n')
        
        curiositySlider = ttk.Scale(self,from_= 1 ,to=0, orient='vertical', command=self.curiositySlider_changed, 
                                 variable=self.curiositycurrent_value)
        curiositySlider.grid(column=1,row=0,sticky='we')
        curiositycurrent_value_label = ttk.Label(self, text='Curiosity:')       
        curiositycurrent_value_label.grid(row=1, column = 1,  sticky='n', ipadx=10, ipady=10)
        self.curiosityvalue_label = ttk.Label(self, text=self.curiosityget_current_value())
        self.curiosityvalue_label.grid(row=4, column = 1,  sticky='n')
        
        self.response_label = ttk.Label (self, text = "Wait for Serial to start")
        self.response_label.grid(column=2,row=0,sticky='we')

        """
        Buttons
        """
        self.startUsbButton = ttk.Button(self, text="Start Serial", command = self.serialStart)
        self.startUsbButton.grid(column = 0, row = 6, sticky = 'we')  
        self.stopButton = ttk.Button(self, text="Exit", command = self.stop)
        self.stopButton.grid(column = 0, row = 8, sticky = 'we')  
        self.sendEEGButton = ttk.Button(self, text="Send EEG", command = self.sendEEG)        
        self.sendEEGButton.grid(column = 1, row = 7, sticky = 'we' )   
        self.sendEEGButton["state"] = tk.DISABLED
        
        """
        Checkboxes
        """ 

        
        """
        Serial Port
        """
        portLabel =tk.Label(self, text = "Port")
        portLabel.grid(column = 1, row = 6, sticky ='nwe')
        self.portEntry =  tk.Entry(self)
        self.portEntry.grid(column = 2, row = 6, sticky ='nwe')
        self.portEntry.insert( -1, "COM4")
        speedLabel =tk.Label(self, text = "Speed")
        speedLabel.grid(column = 3, row = 6, sticky ='nwe')
        self.speedEntry =  tk.Entry(self)
        self.speedEntry.grid(column = 4, row = 6, sticky ='nwe')
        self.speedEntry.insert(-1, "9600")
        
        self.update()
    
    def serialStart(self):
        self.port = self.portEntry.get()
        self.speed = self.speedEntry.get()
        
        try:
            self.arduino = serial.Serial(self.port, self.speed)
            
            response = str(self.arduino.read().decode())
            while not 'i' in response:
                response = str(self.arduino.read().decode())
            print("Connection to " + self.port + " established succesfully!\n")
            self.arduinoStarted = True # inform main loop that serial communication is there
            self.arduino.timeout = 0
            self.arduino.flush()  # make sure buffer is emptied. There may be noise on the line due to USB connection
            self.sendEEG() # To start the handshake with the Arduino a 'r' response is needed and forced by sending this command
            self.startUsbButton["state"] = tk.DISABLED
            
        except Exception as e:
            print(e)          
    
    def excitementget_current_value(self):
        return '{: .2f}'.format(self.excitementcurrent_value.get())
    
    def  excitementSlider_changed(self, event):
       self.excitementvalue_label.configure(text=self.excitementget_current_value())
       
    def curiosityget_current_value(self):
        return '{: .2f}'.format(self.curiositycurrent_value.get())
    
    def  curiositySlider_changed(self, event):
       self.curiosityvalue_label.configure(text=self.curiosityget_current_value())

    def sendEEG(self):        
            freString = str(self.excitement)   
            freString += ','
            freString += str(self.curiosity)
            freString += '\n' 
            self.arduino.write(freString.encode())
            print(self.excitement, ',', self.curiosity)                

if __name__ == '__main__':
    app = AlphaSource()
    app.mainloop()
