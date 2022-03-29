# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 20:30:03 2022
Adapted 14 MArch

@author: Erwin
"""
from threading import Thread, Event
from time import sleep
import time
import tkinter as tk
from tkinter import ttk
from Fp1Fp2EEGControl import EEGSensor
from Fp1Fp2ArduinoControl import arduinoController

class sharedData:
    def __init__(self, data = None):
        self.data = data

    def get(self):
        return self.data

    def set(self,data):
        self.data = data

class main(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exciteIdx = 0
        self.exciteInit = 0.5       
        self.curiosityInit = 0.5
        self.curiosityIdx = 1
        self.maximumInit = 1
        self.defaultStreak = 3
        self.stepValue = 0.1
        self.scaleValue = 1.0
        self.EEGStarted = False
        self.serialStarted = False
        self.moodData = sharedData([self.exciteInit, self.curiosityInit])
        self.paramSelection = sharedData(0)
        self.finishRunning = Event()
        self.dataSent = Event()
        self.programRunning = True
        self.ledONTime = time.time()
        self.initTheGui() 
        
        
    def mainloop(self):
        """
        Wait for EEG and USB connection to be established before starting Data Acq
        """ 
        while self.programRunning:
            self.update() 
            sleep(0.2)
            if (self.EEGStarted and self.serialStarted):
                self.runDataAcq() 
                 
    """
        Data Acq happens in the EEG module, this loop just takes care of the displaying
        and showing the selected parameter
    """

    def runDataAcq(self):       
        while self.programRunning:
            if time.time() - self.ledONTime  > 0.1:
                self.startUsbButton.configure(bg="green")          
            self.showParamSelection() 
            if self.dataSent.is_set():
                self.dataSent.clear()
                self.startUsbButton.configure(bg="yellow")  
                self.ledONTime = time.time()               
            self.update()   
            #sleep(0.1)
                
    def stopProgram(self):   
            self.finishRunning.set()    # tells the other threads to stop running (if they are)
            self.programRunning = False    
            if self.serialStarted:
                self.arduinoThread.join()
            if self.EEGStarted:
                self.EEGThread.join()
            self.destroy()
            
    def setActions(self):
        if self.EEGStarted:
            self.eegInput.setClassification(self.downValue.get(), self.down1Value.get(), self.upValue.get(), self.up1Value.get())

    def updateStreakSliderValue(self, event):
        streakValue =  self.streakSlider.get()
        if self.EEGStarted:
            self.eegInput.setRequiredStreak(streakValue)
            
    def updateScaleSliderValue(self, event):
        self.scaleValue =  self.scaleSlider.get()
        if self.serialStarted:
            self.arduinoInput.setScaling(self.scaleValue)       

    def startArduino(self):
        if not self.serialStarted:
            port = self.portEntry.get()
            speed = self.speedEntry.get()          
            self.arduinoInput = arduinoController(port, speed) # default values, can later be set via GUI
            if self.arduinoInput.checkArduinoStarted():
                self.serialStarted = True
                self.startUsbButton.configure(bg="green") 
                self.arduinoThread = Thread(target=self.arduinoInput.run, args = (self.finishRunning, self.moodData, self.dataSent ))
                self.arduinoThread.start() 
            else:
                print ("In GUI Arduino not started")
                self.startUsbButton.configure(bg="red") 
        
    def startEEG(self):
        if not self.EEGStarted:
            self.eegInput = EEGSensor()
            if self.eegInput.checkEEGStarted():
                self.EEGThread = Thread(target=self.eegInput.run, args = (self.finishRunning, self.moodData, self.paramSelection, self.stepValue ))
                self.EEGThread.start()
                self.EEGStarted = True
                self.startEEGButton.configure(bg="green")
            else:
                print("In GUI EEG not started")
                self.startEEGButton.configure(bg="red")
            
    def updateStepSliderValue(self, event):
        stepValue =  self.stepSlider.get()
        if self.serialStarted:
            self.stepValue = 1 / stepValue
            
            
    def showParamSelection(self):
            thisMood = self.moodData.get()     
            self.excitementBar['value'] = thisMood[self.exciteIdx]
            self.curiosityBar['value'] = thisMood[self.curiosityIdx]  
            selectedParam = self.paramSelection.get()
            if selectedParam == self.exciteIdx:
               self.excitement_label.config(bg="green")
               self.curiosity_label.config(bg="grey")
            if selectedParam == self.curiosityIdx:
               self.excitement_label.config(bg="grey")
               self.curiosity_label.config(bg="green") 
               
    def setInterpretation(self):
        self.up = self.classes.get('eyes_up')
        self.down = self.classes.get('eyes_down')    
        self.up1 = self.classes.get('teeth')
        self.down1 = self.classes.get('blink')
        
    def disable_event(self):
        pass
    
    def pauseAcq(self):        
        if self.EEGStarted and self.serialStarted:
            if self.pauseButton.config('text')[-1] == 'Running':
                self.eegInput.setPaused(True)
                self.arduinoInput.setPaused(True)
                self.pauseButton.config(text='Paused')
            else:
                self.pauseButton.config(text='Running') 
                self.eegInput.setPaused(False) 
                self.arduinoInput.setPaused(False)                
                
    
    def resetCuriosity(self):
        if self.EEGStarted:
             self.curiosityBar['value'] = 0.5 * self.maximumInit
             self.eegInput.setMoodValue(self.curiosityIdx, 0.5 * self.maximumInit)
  
    def resetExcite(self):
        if self.EEGStarted:
             self.excitementBar['value'] = 0.5 * self.maximumInit
             self.eegInput.setMoodValue(self.exciteIdx, 0.5 * self.maximumInit)
            
             
    def initTheGui(self):
        """
        Main Panel settings
        """
        self.title("Excitement Curiosity simulator")
        self.geometry("800x600")
        self.resizable(width = True, height = True)
        self.attributes("-topmost", True)
        self.emptyLabel = tk.Label(self,  width=20, height=2)
        self.emptyLabel.grid(column = 0, row = 5)
        self.empty1Label = tk.Label(self,  width=20, height=1)
        self.empty1Label.grid(column = 0, row = 9)
        self.stopButton = tk.Button(self, text="Stop Program", command = self.stopProgram)
        self.stopButton.grid(column = 3, row = 8, sticky = 'we') 
        self.protocol("WM_DELETE_WINDOW", self.disable_event)
        
        """
        Pause button definition
        """
        self.pauseButton = tk.Button(self, text="Running", width=10, command = self.pauseAcq)
        self.pauseButton.grid(column = 2, row = 8, sticky = 'we')
        
        """
        Progressbars plus label
        """
        self.excitementBar = ttk.Progressbar(self, orient='vertical', length=300, mode='determinate', maximum = self.maximumInit)
        self.excitementBar['value'] = self.exciteInit
        self.excitementBar.grid(column=0,row=0,sticky='we')
        self.excitement_label = tk.Label(self, text="Excitement level", width=20, height=2)
        self.excitement_label.grid(row=4, column = 0,  sticky='n')
        
        self.curiosityBar = ttk.Progressbar(self, orient='vertical', length=300, mode='determinate', maximum = self.maximumInit)
        self.curiosityBar['value'] = self.exciteInit
        self.curiosityBar.grid(column=1,row=0,sticky='we')
        self.curiosity_label = tk.Label(self, text="Curiosity level", width=20, height=2)
        self.curiosity_label.grid(row=4, column = 1,  sticky='n') 
        self.resetCuriosityButton = tk.Button(self, text="Reset Curiosity", command = self.resetCuriosity)
        self.resetCuriosityButton.grid(row=7, column = 2,  sticky='we') 
        self.resetExcitementButton = tk.Button(self, text="Reset Excitement", command = self.resetExcite)
        self.resetExcitementButton.grid(row=6, column = 2,  sticky='we')        
        
        
        """
        Serial Interface settings
        """
        self.portLabel =tk.Label(self, text = "Serial Port")
        self.portLabel.grid(column = 0, row = 6, sticky ='nwe')

        self.portEntry =  tk.Entry(self)
        self.portEntry.grid(column = 1, row = 6, sticky ='nwe')
        self.portEntry.insert( -1, "COM3")
        self.speedLabel =tk.Label(self, text = "Serial Speed")
        self.speedLabel.grid(column = 0, row = 7, sticky ='nwe')
        self.speedEntry =  tk.Entry(self)
        self.speedEntry.grid(column = 1, row = 7, sticky ='nwe')
        self.speedEntry.insert(-1, "9600")
        self.startUsbButton = tk.Button(self, text="Start Serial", command = self.startArduino)
        self.startUsbButton.grid(column = 0, row = 8, sticky = 'we')  
        
        """
        StepSlider settings
        """
        self.stepSlider = tk.Scale(self, from_= 5, to = 25, orient="vertical", length = 300, sliderlength = 20)
        self.stepSlider.bind("<ButtonRelease-1>", self.updateStepSliderValue)
        self.stepSlider.set(self.maximumInit)
        self.stepSlider.grid(column = 2, row = 0, sticky = 'n') 
        self.slider_label = tk.Label(self, text="nbr steps", width=20, height=2)
        self.slider_label.grid(row=4, column = 2,  sticky='n')
        
        """
        ScalingSlider settings
        """ 
        self.scaleSlider = tk.Scale(self, from_= 0.1, to = 2.0, orient="vertical", resolution = 0.05, length = 300, sliderlength = 20)
        self.scaleSlider.bind("<ButtonRelease-1>", self.updateScaleSliderValue)
        self.scaleSlider.set(self.scaleValue)
        self.scaleSlider.grid(column = 4, row = 0, sticky = 'n') 
        self.scale_label = tk.Label(self, text="arduino scale", width=20, height=2)
        self.scale_label.grid(row=4, column = 4,  sticky='n')
        """
        EEG settings
        """  
        self.startEEGButton = tk.Button(self, text="Start EEG", command = self.startEEG)
        self.startEEGButton.grid(column = 1, row = 8, sticky = 'we')  
        self.eegValues = ['blink', 'teeth', 'eyes_up', 'eyes_down']               
        self.upValue = tk.StringVar()
        self.up1Value = tk.StringVar()
        self.downValue = tk.StringVar()
        self.down1Value = tk.StringVar()   
        
        self.streakSlider = tk.Scale(self, from_= 1, to = 5, orient="vertical", length = 300, sliderlength = 20)
        self.streakSlider.bind("<ButtonRelease-1>", self.updateStreakSliderValue)
        self.streakSlider.set(self.defaultStreak)
        self.streakSlider.grid(column = 3, row = 0, sticky = 'n') 
        self.streak_label = tk.Label(self, text="streaks", width=20, height=2)
        self.streak_label.grid(row = 4, column = 3,  sticky='nw')
        
        self.up_cb = ttk.Combobox(self, textvariable=self.upValue)
        self.up_cb['values'] = self.eegValues
        self.up_cb.current(2)
        self.up_cb['state'] = 'readonly'


        self.up1_cb = ttk.Combobox(self, textvariable=self.up1Value)
        self.up1_cb['values'] = self.eegValues
        self.up1_cb.current(1)
        self.up1_cb['state'] = 'readonly'

        
        self.down_cb = ttk.Combobox(self, textvariable=self.downValue)
        self.down_cb['values'] = self.eegValues
        self.down_cb.current(3)
        self.down_cb['state'] = 'readonly'


        self.down1_cb = ttk.Combobox(self, textvariable=self.down1Value)
        self.down1_cb['values'] = self.eegValues
        self.down1_cb.current(0)
        self.down1_cb['state'] = 'readonly'
        
        self.up_cb.grid(column = 1, row = 10, sticky = 'nwe')        
        self.up1_cb.grid(column = 1, row = 11, sticky = 'nwe')    
        self.down_cb.grid(column = 1, row = 12, sticky = 'swe')        
        self.down1_cb.grid(column = 1, row = 13, sticky = 'swe')
        self.upLabel =tk.Label(self, text = "Up: ")
        self.up1Label =tk.Label(self, text = "Up1: ")  
        self.downLabel =tk.Label(self, text = "Down: ")    
        self.down1Label =tk.Label(self, text = "Down1: ")   
        self.upLabel.grid(column = 0, row = 10, sticky = 'nwe') 
        self.up1Label.grid(column = 0, row = 11, sticky = 'nwe') 
        self.downLabel.grid(column = 0, row = 12, sticky = 'nwe')         
        self.down1Label.grid(column = 0, row = 13, sticky = 'nwe')             
        self.setActionsButton = tk.Button(self, text="Set Actions", command = self.setActions)
        self.setActionsButton.grid(column = 2, row = 13, sticky = 'we')          

        self.update()    
             
      
if __name__ == '__main__':
    app = main()
    app.mainloop()           