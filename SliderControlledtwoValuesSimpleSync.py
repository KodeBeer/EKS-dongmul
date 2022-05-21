# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 16:32:20 2021

@author: Erwin
"""

import tkinter as tk
from tkinter import ttk
#from tkinter import IntVar

import serial
#import time

class AlphaSource(tk.Tk):
   
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initTheGui() 
        self.arduinoStarted = False
        self.measuredone = True
        self.measureLoop()
        self.arduino = serial.Serial()
        self.arduinoReady = False
           
    def measureLoop(self):            
        if self.arduinoStarted:  # This is after communication with Arduino was succesfully started
            while self.arduino.inWaiting():
                response = str(self.arduino.readline().decode())
                self.message_label.config(text=response)
                #print("Message received: " + response)                
            self.update()  # Make sure GUI is ready and up to date    
       
        self.after(5, self.measureLoop) # restart measure loop after 50 msec
      
    def stop(self):
        self.arduino.close()
        self.destroy()
        
    def initTheGui(self):
        self.title("Excitement Curiosity simulator")
        self.geometry("600x600")
        self.resizable(width = True, height = True)
        # slider current value
        self.excitementcurrent_value = tk.DoubleVar()
        self.curiositycurrent_value = tk.DoubleVar()   
        self.calibPoscurrent_value = tk.DoubleVar()
        self.calibNegcurrent_value = tk.DoubleVar()    

        self.excitementvalue_label = ttk.Label(self, text=self.excitementget_current_value())
        self.excitementvalue_label.grid(row=4, column = 0,  sticky='n')               
        excitementSlider = ttk.Scale(self,from_= 1.0 ,to = 0.1, orient='vertical', length = 250,  
                                     command=self.excitementSlider_changed, variable=self.excitementcurrent_value)
        excitementSlider.set(0.3)
        excitementSlider.grid(column=0,row=0,sticky='we')
        excitementcurrent_value_label = ttk.Label(self, text='Excitement:')       
        excitementcurrent_value_label.grid(row=1, column = 0,  sticky='n', ipadx=10, ipady=10)
        
        curiositySlider = ttk.Scale(self,from_= 1.0 ,to = 0.1, orient='vertical', length = 250, 
                                    command=self.curiositySlider_changed, variable=self.curiositycurrent_value)
        self.curiosityvalue_label = ttk.Label(self, text=self.curiosityget_current_value())
        self.curiosityvalue_label.grid(row=4, column = 1,  sticky='n')               
        curiositySlider.set(0.3)
        curiositySlider.grid(column=1,row=0,sticky='we')
        curiositycurrent_value_label = ttk.Label(self, text='Curiosity:')       
        curiositycurrent_value_label.grid(row=1, column = 1,  sticky='n', ipadx=10, ipady=10)

        calibPosSlider = ttk.Scale(self,from_= 2.0, to = 0.1, orient='vertical', length = 250,  
                                   command=self.calibPosSlider_changed, variable=self.calibPoscurrent_value)
        
        self.calibPosvalue_label = ttk.Label(self, text=self.calibPosget_current_value())
        self.calibPosvalue_label.grid(row=4, column = 2,  sticky='n')        
        calibPosSlider.set(0.5)
        calibPosSlider.grid(column=2,row=0,sticky='we')
        calibPoscurrent_value_label = ttk.Label(self, text='CalibPos:')       
        calibPoscurrent_value_label.grid(row=1, column = 2,  sticky='n', ipadx=10, ipady=10)

        calibNegSlider = ttk.Scale(self,from_= 2.0, to = 0.1, orient='vertical', length = 250,  
                                   command=self.calibNegSlider_changed, variable=self.calibNegcurrent_value)
        
        self.calibNegvalue_label = ttk.Label(self, text=self.calibNegget_current_value())
        self.calibNegvalue_label.grid(row=4, column = 3,  sticky='n') 
        calibNegSlider.set(1.2)
        calibNegSlider.grid(column=3,row=0,sticky='we')
        calibNegcurrent_value_label = ttk.Label(self, text='CalibNeg:')       
        calibNegcurrent_value_label.grid(row=1, column = 3,  sticky='n', ipadx=10, ipady=10)
               
        self.response_label = ttk.Label (self, text = "Serial not started")
        self.response_label.grid(column=0,row=8,sticky='we')
        self.message_label = ttk.Label (self, text = "None")
        self.message_label.grid(column=2,row=8,sticky='we')

        """
        Buttons
        """
        self.startUsbButton = ttk.Button(self, text="Start Serial", command = self.serialStart)
        self.startUsbButton.grid(column = 0, row = 6, sticky = 'we')  
        self.sendEEGButton = ttk.Button(self, text="Send EEG", command = self.sendEEG)        
        self.sendEEGButton.grid(column = 0, row = 10, sticky = 'we' )   
        self.sendCalibButton = ttk.Button(self, text="Send Calib", command = self.sendCalib)        
        self.sendCalibButton.grid(column = 0, row = 12, sticky = 'we' )         
        self.stopButton = ttk.Button(self, text="Exit", command = self.stop)
        self.stopButton.grid(column = 0, row = 15, sticky = 'we')  
        
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
        self.speedEntry.insert(-1, "115200")
        
        self.update()
    
    def serialStart(self):
        self.port = self.portEntry.get()
        self.speed = self.speedEntry.get()
        
        try:
            self.arduino = serial.Serial(self.port, self.speed)
            self.arduino.reset_input_buffer()          
            response = str(self.arduino.read().decode())
            while not 'i' in response:
                response = str(self.arduino.read().decode())
            print("Connection to " + self.port + " established succesfully!\n")

            self.arduino.timeout = 0.5
            self.arduino.flush()  # make sure buffer is emptied. There may be noise on the line due to USB connection
            self.response_label.config(text="Serial started")
            self.startUsbButton["state"] = tk.DISABLED
            self.arduinoStarted = True # inform main loop that serial communication is there
            
        except Exception as e:
            print(e)          
    
    def excitementget_current_value(self):
        return '{: .2f}'.format(self.excitementcurrent_value.get())
    
    def excitementSlider_changed(self, event):
        self.excitementvalue_label.configure(text=self.excitementget_current_value())
       
    def curiosityget_current_value(self):
        return '{: .2f}'.format(self.curiositycurrent_value.get())
    
    def curiositySlider_changed(self, event):
        self.curiosityvalue_label.configure(text=self.curiosityget_current_value())

    def calibPosget_current_value(self):
        return '{: .2f}'.format(self.calibPoscurrent_value.get())       

    def calibPosSlider_changed(self, event):
        self.calibPosvalue_label.configure(text=self.calibPosget_current_value())        

    def calibNegget_current_value(self):
        return '{: .2f}'.format(self.calibNegcurrent_value.get())       

    def calibNegSlider_changed(self, event):
        self.calibNegvalue_label.configure(text=self.calibNegget_current_value())  

    def sendEEG(self):  
        self.excitement = self.excitementcurrent_value.get()
        self.excitement = round(self.excitement, 4)
        self.curiosity = self.curiositycurrent_value.get()
        self.curiosity = round(self.curiosity, 4) 
        freString = '0;' #Command to update speed and volume
        freString += str(self.excitement)   
        freString += ','
        freString += str(self.curiosity)
        #freString += '\n' 
        #print("Send Excitement + curiosity: " + freString)
        self.arduino.write(freString.encode())
        
    def sendCalib(self):
        self.calibPos = self.calibPoscurrent_value.get()
        self.calibPos = round(self.calibPos, 4)
        self.calibNeg = self.calibNegcurrent_value.get()
        self.calibNeg = round(self.calibNeg, 4)
        freString = '1;'
        freString += str(self.calibPos)
        freString += ','
        freString += str(self.calibNeg)   
        self.arduino.write(freString.encode())        
              
if __name__ == '__main__':
    app = AlphaSource()
    app.mainloop()
