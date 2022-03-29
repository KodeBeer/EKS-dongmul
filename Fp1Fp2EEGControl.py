# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 09:50:13 2022

@author: Erwin
"""

from time import sleep
#import argparse
#from pythonosc import udp_client
import numpy as np

from brainaccess import motion_classifier  # import MotionClassifier algorithm

class EEGSensor:
    def __init__(self, required_streak=3, drop_data_after_action=True):
        print("Initializing MotionClassifier and starting acquisition")
        self.paramSelection = 0
        self.maxAllowedValue = 1
        #self.classList = ['calm', 'blink', 'double_blink', 'teeth', 'eyes_up', 'eyes_down' ]
        self.classes = {'calm': 0, 'blink': 1, 'double_blink': 2, 'teeth': 3, 'eyes_up': 4, 'eyes_down': 5 }
        # this builds a reverse dictionary where the index (key) leads to a class name (value)
        self.idx_to_class = { val: key for (key, val) in self.classes.items()}   
        self.required_class_confidences = { 'calm': 0.8, 'blink': 0.8, 'double_blink': 0.8, 'teeth': 0.8, 'eyes_up': 0.6, 'eyes_down': 0.8  }
        self.required_streak = required_streak      
        self.previous_prediction = 'calm'        
        self.prediction_streak = 0
        self.drop_data_after_action = drop_data_after_action  
        self.inEEGStarted = False
        self.switchLed = self.classes.get('double_blink')
        self.up = self.classes.get('eyes_up')
        self.down = self.classes.get('eyes_down')    
        self.up1 = self.classes.get('teeth')
        self.down1 = self.classes.get('blink')
        self.stepSize = 0.1
        self.paused = False

        if motion_classifier.initialize(fp1Idx=0, fp2Idx=2):
            motion_classifier.start()
            self.inEEGStarted = True

    def setRequiredStreak(self, requiredStreak):
        self.required_streak = requiredStreak

    def checkEEGStarted(self):
        return self.inEEGStarted
        
    def run(self, finish, data, paramSelection, stepSize):
        self.moodData = data
        self.paramSelection = paramSelection
        self.stepSize = stepSize

        while not finish.is_set():
            if not self.paused:
                probs, classes = motion_classifier.predict()
                # sort probabilities in ascending order and gather sorted indices
                sorted_indices = np.argsort(probs)
                
                # print the 2 predictions with the highest probabilities
                self.print_prediction(sorted_indices[-1], probs[sorted_indices[-1]])
    
                # take the highest probability prediction and its confidence
                prediction = sorted_indices[-1]
                confidence = probs[prediction]
                self.process_prediction(prediction, confidence)
                #sleep(0.5)
                #print ("Evaluating inside EEG run def")
            
    def reset_state(self):
        self.prediction_streak = 0

        if self.drop_data_after_action:
            motion_classifier.discard_data()
        # we find that a small pause either way makes this demo more stable
        else:
            sleep(2)
            
    def process_prediction(self, prediction, confidence):
        cl = self.idx_to_class[prediction]  # get class name
         
        # increment prediction_streak or set it to 1 if the streak ended
        self.prediction_streak = self.prediction_streak + 1 if self.previous_prediction == cl else 1 
        self.previous_prediction = cl

        if self.prediction_streak >= self.required_streak and self.prediction_is_confident(confidence, cl):            
            """
            2,4,5 select up down
            """
            if self.prediction_is_confident(confidence, cl):
                #print("prediction is:  " + str(prediction))

                if prediction == self.switchLed:
                    self.paramSelection.set(1 - self.paramSelection.get())
                    print("Switch LED")
   
                if (prediction == self.down or prediction == self.down1) :
                    mood = self.moodData.get()
                    if mood[self.paramSelection.get()] > self.stepSize:
                        mood[self.paramSelection.get()] -= self.stepSize                                              
                    else:
                        mood[self.paramSelection.get()] = 0.05                        
                    self.moodData.set(mood)
                    print("Level DOWN")
                  
                if (prediction == self.up or prediction == self.up1)  :
                    mood = self.moodData.get()
                    if mood[self.paramSelection.get()] < self.maxAllowedValue -self.stepSize:                    
                        mood[self.paramSelection.get()] += self.stepSize
                    else:
                        mood[self.paramSelection.get()] = self.maxAllowedValue
                        self.moodData.set(mood) 
                    print ("Level UP")
                         
            action_was_performed = True
            if action_was_performed:
                self.reset_state()   
                
    
    # determine if the prediction's confidence was sufficient (the confidences are pre-set and can be adjusted by changing required_class_confidences)
    def prediction_is_confident(self, confidence, class_name):
        if confidence < self.required_class_confidences[class_name]:
            #print("Unconfident prediction, Skipping")
            return False
        return True
    
    def setClassification(self, down, down1, up, up1):
        self.up = self.classes.get(up)
        self.down = self.classes.get(down)    
        self.up1 = self.classes.get(up1)
        self.down1 = self.classes.get(down1)
            
    def print_prediction(self, prediction, confidence):       
        print("Guess: {0}  confidence: {1}% ".format(
            str(self.idx_to_class[prediction]).upper(), round(confidence * 100, 2)))
            #str(self.idx_to_class[second_prediction]).upper(), round(second_confidence * 100, 2))))       
    
    def setMaxAllowedValue(self, maxVal = 1):
        self.maxAllowedValue = maxVal
        
    def setMoodValue(self, selectMood, theValue):
        mood = self.moodData.get()                   
        mood[selectMood] = theValue    
        
    def setPaused(self, paused):
        self.paused = paused
        print ("EEG Paused is: " + str(self.paused))


# helper method to calculate Root Mean Square
def rms(data):
    return np.sqrt(np.mean(data**2))
