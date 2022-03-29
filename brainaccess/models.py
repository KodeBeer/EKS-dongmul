import numpy as np
from ctypes import *
from brainaccess.utilities import *
from brainaccess.ba_ctypes import *

# define python types
class EEGData():
    """A python object holding EEG data. Used in data saving/loading.
    
    Attributes:
        **sampling_frequency** (double): data sampling frequency in Hz.
        
        **labels** (list [string]): channel labels.
        
        **measurements** (numpy array [float64]): EEG data (number of channels x time points).
        
        **accelerometer_data** (numpy array [float64]): accelerometer data (3 x time points).
    """
    def __init__(self):        
        self.measurements = np.empty(0, dtype = np.float64)
        self.accelerometer_data = np.empty(0, dtype = np.float64)
        self.sampling_frequency = 125.0
        self.labels = [] 

class EEGDataStream():
    """A python object defining a collection of BrainAccess EEG hardware measurement samples and
 stream status information.
        
    Attributes:
        **num_samples** (int): number of acquired data samples.
        
        **stream_disrupted** (bool): True if data stream with Brain Access EEG hardware was disrupted and some samples might be lost. False otherwise.
        
        **reading_is_too_slow** (bool): True if data is read too slowly (i.e. `getData` methods are called too infrequently). In this case internal BrainAccess Core buffer gets full and some data might be lost. False otherwise.
        
        **connection_lost** (bool): True if wifi connection with Brain Access EEG hardware has been lost, False if everything is ok.
        
        **measurements** (numpy array [float64]): EEG data (number of channels x time points), values in uV. Note that channel order in measurements is always in ascending order based on channel indices. We recommend users to store channel indices in ascending order in their code as well, to prevent confusion and mishaps.
        
        **lead_status** (numpy array [int]): lead statuses of active channels for each time point (number of channels x time points), values: 0-connected, 1-not connected. Note that channel order in leadStatus is always in ascending order based on channel indices. We recommend users to store channel indices in ascending order in their code as well, to prevent confusion and mishaps.
        
        **accelerometer_data** (numpy array [float64]): accelerometer data (3 x time points), values in fraction of `g`.  
    """ 
    
    def __init__(self):   
        self.num_samples = 0
        self.stream_disrupted = False
        self.reading_is_too_slow = False
        self.connection_lost = False
        self.accelerometer_data = np.empty(0, dtype = np.float64)
        self.measurements = np.empty(0,dtype = np.float64)
        self.lead_status = np.empty(0, dtype = np.int)
        
class FourierTransform():
    """A python object containing spectrum data calculated using FFT.
        
    Attributes:
        **frequencies** (numpy array [float64]): a frequency axis for calculated spectrum.
        
        **spectrum** (numpy array [complex]): the calculated spectrum.
        
        **magnitudes** (numpy array [float64]): the magnitude of the spectrum, normalized to the number of samples.
        
        **phases** (numpy array [float64]): the phase values of the spectrum.
    """ 
    def __init__(self):
        self.frequencies = np.empty(0, dtype = np.float64)
        self.spectrum = np.empty(0, dtype = np.complex)
        self.magnitudes = np.empty(0, dtype = np.float64)
        self.phases = np.empty(0, dtype = np.float64)
         
class DetrendSettings():
    """A python object containing parameters for signal detrend algorithm.
    
    Attributes:
        **is_active** (bool): True if used, False otherwise.

        **polynomial_degree** (int): Order of polynomial curve used to remove data trend.
    """
    def __init__(self):
        self.is_active = True
        self.polynomial_degree = 1

class FilterSettings():
    """A python object containing signal filter parameters.
    
    Attributes:
        **is_active** (bool): True if used, False otherwise.
        
        **type** (string): filter type, possible options: bandpass, bandstop, highpass and lowpass.
        
        **order** (int): filter order.
        
        **min_frequency** (double): low cut-off frequency for band filters and cut-off frequency for highpass filter
        
        **max_frequency** (double): high cut-off frequency for band filters and cut-off frequency for lowpass filter
    """
        
    def __init__(self):
        self.is_active = True
        self.type = "bandpass"
        self.order = 2
        self.min_frequency = 1
        self.max_frequency = 24
      
class WindowSettings():
    """A python object containing temporal window parameters.
    
    Attributes:
        **is_active** (bool): True if used, False otherwise.
        
        **type** (string): window type, possible options: tukey or hann.
        
        **tukey_alpha** (double): tukey window parameter.
    """
    def __init__(self):
        self.is_active = True
        self.type = "tukey"
        self.tukey_alpha = 0.2