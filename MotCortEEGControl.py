# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 09:50:13 2022

@author: Erwin
"""
import random
from time import sleep

class EEG():
    def __init__(self):
        pass
    
    def setup(self):
        pass
    
    def run(self, excitement, curiosity, finish):
        while  finish.value == 0:
            excitement.value = 0
            curiosity.value = 1
            sleep(1)
            excitement.value = 1
            curiosity.value = 0
            sleep(1)
            