# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 09:50:13 2022

@author: Erwin
"""
import random
from time import sleep
import brainaccess as ba
import numpy as np
from sys import exit
import matplotlib.pyplot as plot

# Initialize the module


class EEG():
    def __init__(self):
        self.sampleFreq = 125.0
        self.bufferTime = 1.0
        self.eegStarted = False
        self.channel_numbers = [0, 1]
        self.scounter = 0
        self.goUp = True

    
    def setup(self):
        logFile = open("eeglog.txt", "w")
        response = ba.initialize()
        if response != 0:
            self.eegStarted = False
            logFile.write("error init BA \n")
            return
        logFile.write("BA is init \n")
        self.eegStarted = True
        ba.set_sampling_frequency(self.sampleFreq)

        #electrode_labels = ["Fp1", "Fp2"]
        self.bias_channel_numbers = [0]
        ba.set_channels(self.channel_numbers, self.bias_channel_numbers)
 
        time = np.arange(0, self.bufferTime, 1.0/self.sampleFreq)
        self.data = np.zeros((len(self.channel_numbers), len(time)))
        self.lead_status = np.zeros((len(self.channel_numbers), len(time)))
        self.data_accel = np.zeros((3, len(time)))
        ba.set_preprocessing_sampling_frequency(self.sampleFreq)
        detrend = ba.DetrendSettings()  # will get default settings for detrender
        ba.set_detrend_settings(detrend)
        filt = ba.FilterSettings()
        filt.type = "bandpass"
        filt.order = 2
        filt.min_frequency = 7
        filt.max_frequency = 20
        ba.set_filter_settings([filt])
        self.data_processed = np.zeros((len(self.channel_numbers), len(time)))
        self.num_samples_to_acquire = 20
        self.tot_num_samples = time * self.sampleFreq
        logFile.write("setup is completed \n")
        logFile.close()

    def reportIssue(self, issue, eegStatus, finish):
        eegStatus.value = issue
        finish.value = 2
    
    def run(self, excitement, curiosity, finish, eegStatus):
        self.setup() 
        logFile = open("eeglog.txt", "a")
        logFile.write("Setup Completed and eegStarted is: ")
        logFile.write(str(self.eegStarted))
        logFile.write("\n")
        if self.eegStarted:
            ba.start_acquisition()
            logFile.write("Started acq \n")
            logFile.write("finish value = ") 
            logFile.write(str(finish.value)) 
            while  finish.value == 0:
                
                eeg_data = ba.get_data_samples(self.num_samples_to_acquire)
                if eeg_data.connection_lost:
                    self.reportIssue(1, eegStatus, finish)
            
                if eeg_data.stream_disrupted:
                    self.reportIssue(2, eegStatus, finish)
            
                if eeg_data.reading_is_too_slow:
                    self.reportIssue(3, eegStatus, finish)
            
                #shift the buffers and append the newly retrieved data
                
                for m in range(0, len(self.channel_numbers)):
                    self.data[m] = np.roll(self.data[m], -eeg_data.num_samples)
                    self.data[m, -eeg_data.num_samples:] = eeg_data.measurements[m]
            
                # preprocess the eeg data
                for m in range(0, len(self.channel_numbers)):
                    self.data_processed[m] = ba.preprocess(self.data[m])
                logFile.write("Data block was processed \n")   
                

                for idx in range (len(self.data_processed[0])):
                    self.data_processed[0][idx] = abs(self.data_processed[0][idx])
                    self.data_processed[1][idx] = abs(self.data_processed[1][idx])                    
                
                #self.data_processed[0] = map(abs, self.data_processed[0])
                #self.data_processed[1] = map(abs, self.data_processed[1])
                curiosity.value = sum(self.data_processed[0])  / 5000
                excitement.value = sum(self.data_processed[1])  / 5000
                logFile.write("curios = ")
                logFile.write(str(curiosity.value))
                logFile.write("\n")
                
                if curiosity.value >0.9:
                    curiosity.value = 0.9

                if excitement.value >0.9:
                    excitement.value = 0.9
                """
                if self.goUp == True:
                    if excitement.value < 0.8:
                        excitement.value += 0.05
                    else:
                        self.goUp = False
                    
                if self.goUp == False:
                    if excitement.value >0.1:
                        excitement.value -= 0.05                        
                    else:
                        self.goUp = True
                """            
                    

            ba.stop_acquisition()  
            logFile.close()
        else: 
            eegStatus.value = 3
            

            