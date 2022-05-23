# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 09:50:13 2022

@author: Erwin
"""


import brainaccess as ba
import numpy as np
from scipy.stats import spearmanr
from scipy.signal import find_peaks


class EEG():
    def __init__(self):
        self.sampleFreq = 250.0
        self.fftLength = int(4 * self.sampleFreq)
        self.bufferTime = 1.0
        self.eegStarted = False
        self.channel_numbers = [1, 2]
        self.limitHigh = 0.99
        self.smoothIdx = 0
        self.smoothExcitement = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        self.smoothCuriosity = np.array([0.5, 0.5, 0.5, 0.5, 0.5])

    def findPeakInFourier(self, Signal, threshold):
        fourierTransform = np.fft.rfft(Signal, n = self.fftLength)/len(Signal)          # Normalize amplitude 
        fourierTransform = fourierTransform[range(int(len(Signal)/2))] # Exclude sampling frequency                    
        fourierTransform = np.abs(fourierTransform) ** 2
        indices = find_peaks(fourierTransform)[0]
        highPointValue =  threshold
        highPointIdx = 0
        if len(indices) > 0:
            for peak in indices:
                thisHighPoint = fourierTransform[peak]
                if thisHighPoint > highPointValue:
                    highPointValue = thisHighPoint
                    highPointIdx = peak  
        return highPointIdx 

        

    def fourierAnalysis(self, curiosity, excitement, freqScaler, curiosityScaler, excitementScaler):         
        highPoint = self.findPeakInFourier(self.data_processed[1], curiosityScaler.value)  
        self.smoothCuriosity[self.smoothIdx] = highPoint * freqScaler.value        
        curiosity.value =  np.average(self.smoothCuriosity)         
      
        highPoint = self.findPeakInFourier(self.data_processed[0], curiosityScaler.value)         
        self.smoothExcitement[self.smoothIdx] = highPoint * freqScaler.value  
        excitement.value =  np.average(self.smoothExcitement)       
        self.smoothIdx += 1
        if self.smoothIdx == len(self.smoothExcitement):
            self.smoothIdx = 0
        
        
    def correlation(self, curiosity, excitement, curiosityScaler, excitementScaler):
        curiosity.value, _ =  spearmanr(self.data_processed[0], self.data_processed[1])
        curiosity.value = curiosityScaler.value * abs(curiosity.value)  / 10                  
        for idx in range (len(self.data_processed[0])):                   
            self.data_processed[1][idx] = abs(self.data_processed[1][idx])                                       
        excitement.value = sum(self.data_processed[1])  / excitementScaler.value
    
    def setup(self):
        logFile = open("eeglog.txt", "w")
        logFile.write("Initialize EEG \n")
        response = ba.initialize()
        if response != 0:
            self.eegStarted = False
            logFile.write("error init BA \n")
            return
        logFile.write("BA is init \n")
        self.eegStarted = True
        ba.set_sampling_frequency(self.sampleFreq)
        logFile.write("Started EEG \n")
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
        filt.min_frequency = 1
        filt.max_frequency = 16
        ba.set_filter_settings([filt])
        self.data_processed = np.zeros((len(self.channel_numbers), len(time)))
        self.num_samples_to_acquire = 40
        self.tot_num_samples = time * self.sampleFreq
        logFile.write("Length of processed data: " + str(len(self.data_processed[0])) + "\n" )
        logFile.write("setup is completed \n")
        logFile.close()

    def acquireData(self, eegStatus, finish):
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

    def reportIssue(self, issue, eegStatus, finish):
        eegStatus.value = issue
        finish.value = 2        

    def limitMaxValues(self, curiosity, excitement):
        if curiosity.value > self.limitHigh:
            curiosity.value = self.limitHigh
        if excitement.value > self.limitHigh:
            excitement.value = self.limitHigh
    
    def smooth(self, curiosity, excitement):
        curiosity.value = np.average(self.smoothCuriosity)
        excitement.value = np.average(self.smoothExcitement)
    
    def run(self, excitement, curiosity, finish, eegStatus, excitementScaler, curiosityScaler, freqScaler, algorithm):
        self.setup() 
        logFile = open("eeglog.txt", "a")
        # logFile.write("Setup Completed and eegStarted is: ")
        # logFile.write(str(self.eegStarted))
        # logFile.write("\n")
        if self.eegStarted:
            ba.start_acquisition()
            # logFile.write("Started acq \n")
            # logFile.write("finish value = ") 
            # logFile.write(str(finish.value)) 
            while finish.value == 0:                   
                self.acquireData(eegStatus, finish)
                    
                """
                Do the specific parameter extraction.
                """  
                if algorithm.value == 0:
                    self.correlation(curiosity, excitement, curiosityScaler, excitementScaler)
                    
                if algorithm.value == 1:  
                    self.fourierAnalysis(curiosity, excitement, freqScaler, curiosityScaler, excitementScaler)                     
                    
                self.limitMaxValues(curiosity, excitement)
                             
            ba.stop_acquisition()  
            logFile.close()
        else: 
            eegStatus.value = 3
            logFile.close()
        

            