'''
    Demo of face motion classification using BrainAccess solution.
    Run this script (after ensuring the required dependencies!) to start the demo.
    
    MotionClassifier algorithm, provided in the BrainAccess SDK,
    predicts the probabilities of the following possible actions from 2.5 seconds of measurements:
        calm state (0), 
        blink (1), 
        double blink (2), 
        teeth grind (3), 
        fast eye glance upwards (4), 
        fast eye glance downwards (5)

    The algorithm expects 2 frontal lobe electrodes (Fp1 and Fp2) to be active.
'''


import traceback
import time
import tkinter as tk
from tkinter import ttk
from tkinter import IntVar
import serial
#import os
#import sys
#from os import path
import argparse
from pythonosc import udp_client
import numpy as np

from brainaccess import motion_classifier  # import MotionClassifier algorithm
from sys import exit

class MovSource():
    
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arduino = serial.Serial()

        
    def serialStart(self):
        self.port = 'COM4'
        self.speed = '9600' 
        try:
            self.arduino = serial.Serial(self.port, self.speed)
            time.sleep(2)
            print("Connection to " + self.port + " established succesfully!\n")
        except Exception as e:
            print(e)    
        self.startAcq(self.arduino)

    def startAcq(self, thisArduino):
    
        print("Initializing MotionClassifier and starting acquisition")
    
        # initialize MotionClassifier
        # this sets the required BrainAccess Core settings and prepares internal structures
        # IMPORTANT: set channel indices (fp1Idx, fp2Idx) according to your hardware setup (at the bottom of this script)!    
        if not motion_classifier.initialize(fp1Idx=0, fp2Idx=2):
            exit()
        # start MotionClassifier
        # this starts data acquisition
        motion_classifier.start()
    
    
        # Create the experiment class (responsible for mantaining the state of the demo and issuing actions) and run it.
        # See Experiment.__init__ method for other, optional parameters
        experiment = Experiment(thisArduino)
        experiment.run()


# This is a class responsible for handling the state of the experiment and issuing actions to the BrowserController
class Experiment():
    def __init__(self, thisArduino,  required_streak=3, drop_data_after_action=True):
        self.theArduino = thisArduino
        #self.client = self.setupNetwork() 
        # this dictionary describes the 6 actions that can be recognized by the MotionClassifier
        self.classes = {'calm': 0, 'blink': 1, 'double_blink': 2, 'teeth': 3, 'eyes_up': 4, 'eyes_down': 5 }
        # this builds a reverse dictionary where the index (key) leads to a class name (value)
        self.idx_to_class = { val: key for (key, val) in self.classes.items()}

        # for better user exeperience, it is often useful to inspect the confidence of the algorithm when deciding whether to perform a certain action
        # we suggest using these experimentally determined thresholds.
        # This means, that e.g. action associated with teeth grind will be executed only when the algorithm is more than 95% certain that teeth grind was performed.        
        self.required_class_confidences = { 'calm': 0, 'blink': 0, 'double_blink': 0.9, 'teeth': 0.95, 'eyes_up': 0.8, 'eyes_down': 0.8   }

        # as the required input for MotionClassifier is relatively long (2.5 seconds)
        # if the prediction would be made each 2.5 seconds, the user would end up in situations where
        # the action performed is not always fully captured in the 2.5 seconds input.
        # To avoid this issue, this demo uses prediction without pauses, reusing the larger amount of previously collected measurements on each prediction.
        # However, this means that to arrive at a confident decision, the MotionClassifier needs to predict the same class a number of times in a row.
        # Here, the required streak is 6, however this can depend on the computer running the demo as the prediction speed impacts 
        # the number of predictions made in the 2.5 seconds interval.
        # As such, please try different numbers for required_streak if it feels necessary
        self.required_streak = required_streak
        
        self.previous_prediction = 'calm'        
        self.prediction_streak = 0

        # if set to True,
        # after an action is performed, the collected data is dropped and it is then collected from scratch.
        # We recommend setting this option when running on a fast computer and noticing that an action is performed several times,
        # although the user made a single motion.
        self.drop_data_after_action = drop_data_after_action
        
        

    # runs the experiment
    def run(self):
        while True:
            # ask for a MotionClassifier prediction 
            # when this methods is called, MotionClassifier uses the currently obtained measurements to make a prediction.
            # After a prediction is made, the measurements are not disposed, so a subsequent prediction can be made straight away.
            probs, classes = motion_classifier.predict()
            # sort probabilities in ascending order and gather sorted indices
            sorted_indices = np.argsort(probs)
            
            # print the 2 predictions with the highest probabilities
            self.print_prediction(sorted_indices[-1], probs[sorted_indices[-1]])

            # take the highest probability prediction and its confidence
            prediction = sorted_indices[-1]
            confidence = probs[prediction]
 
            self.process_prediction(prediction, confidence)

    def reset_state(self):
        self.prediction_streak = 0

        # if drop_data_after_action is set
        # discard data currently collected in the BASDK
        # this means that the next prediction will be made after 2.5 seconds 
        if self.drop_data_after_action:
            motion_classifier.discard_data()
        # we find that a small pause either way makes this demo more stable
        else:
            time.sleep(10)

    # takes a made prediction and:
    # - updates the state window
    # - remembers the predicted motion
    # - performs an action if it is required
    def process_prediction(self, prediction, confidence):
        cl = self.idx_to_class[prediction]  # get class name
         

        # increment prediction_streak or set it to 1 if the streak ended
        self.prediction_streak = self.prediction_streak + 1 if self.previous_prediction == cl else 1 
        self.previous_prediction = cl

        # if the required prediction_streak (see notes in the __init__ method) was reached and the confidence is sufficient
        # perform the action associated with the predicted class
        if self.prediction_streak >= self.required_streak and self.prediction_is_confident(confidence, cl):
            # skip if associated action is a non-action
            # print("Performing action: {0}".format(cl))
            # action returns if it was performed
            
            """
            2,4,5 select up down
            """
            if self.prediction_is_confident(confidence, cl):

                if prediction == 2:
                    freString = 's' 
                    print("Switch LED")
                    self.theArduino.write(freString.encode())
    
                if prediction == 3:
                    freString = 'd' 
                    print("Level DOWN")
                    self.theArduino.write(freString.encode())   
                    
                if (prediction == 4) or (prediction == 5):
                    freString = 'u' 
                    print ("Level UP")
                    self.theArduino.write(freString.encode())              
                
            
            action_was_performed = True
            if action_was_performed:
                self.reset_state()   
                
    
    # determine if the prediction's confidence was sufficient (the confidences are pre-set and can be adjusted by changing required_class_confidences)
    def prediction_is_confident(self, confidence, class_name):
        if confidence < self.required_class_confidences[class_name]:
            #print("Unconfident prediction, Skipping")
            return False

        return True
    
    def print_prediction(self, prediction, confidence):
        print("Guess: {0}  confidence: {1}% ".format(
            str(self.idx_to_class[prediction]).upper(), round(confidence * 100, 2) ))
            #str(self.idx_to_class[second_prediction]).upper(), round(second_confidence * 100, 2)))

    def setupNetwork(self):
        # EEG set up, first network then alpha pars
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1",
              help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=5005,
              help="The port the OSC server is listening on")
        args = parser.parse_args()
        return udp_client.SimpleUDPClient(args.ip, args.port)  


# helper method to calculate Root Mean Square
def rms(data):
    return np.sqrt(np.mean(data**2))



if __name__ == "__main__":

    mainloop = MovSource()
    mainloop.serialStart()

