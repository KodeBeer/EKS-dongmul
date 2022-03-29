from ctypes import *
from numpy.ctypeslib import ndpointer 

# define library types
class AccelerometerDataCType(Structure):
    _fields_ = [
        ("x", c_double),
        ("y", c_double),
        ("z", c_double),
    ]
    
class DataDescriptionCType(Structure):
    _fields_ = [
        ("filePath",c_char_p),
        ("separator",c_char),
        ("numChannels",c_int),
        ("numSamples",c_int),
        ("labels",POINTER(c_char_p)),
        ("measurements",POINTER(POINTER(c_double))),
        ("accelerometerData",POINTER(AccelerometerDataCType)),
        ("samplingFrequency",c_double)
    ]

class EEGSamplesCType(Structure):
    _fields_ = [
        ("numSamples", c_int),
        ("numChannels",c_int),
        ("streamDisrupted", c_int),
        ("readingIsTooSlow", c_int),
        ("connectionLost", c_int),
        ("leadStatus",POINTER(POINTER(c_int))),
        ("measurements",POINTER(POINTER(c_double))),
        ("accelerometerData", POINTER(AccelerometerDataCType))
    ]
    
class DetrendingSettingsCType(Structure):
    _fields_ = [
        ("isActive", c_int),
        ("polynomialDegree", c_int)
    ]

class SingleFilterSettingsCType(Structure):
    _fields_ = [
        ("isActive", c_int),
        ("type", c_int),
        ("order", c_int),
        ("minFrequency", c_double),
        ("maxFrequency", c_double)
    ]

class FilteringSettingsCType(Structure):
    _fields_ = [
        ("numFilters", c_int),
        ("filters", POINTER(SingleFilterSettingsCType))
    ]
    
class WindowSettingsCType(Structure):
    _fields_ = [
        ("isActive", c_int),
        ("type", c_int),
        ("tukeyAlpha", c_double)        
    ]
    
class PreprocessingSettingsCType(Structure):
    _fields_ = [
        ("samplingFrequency", c_double),
        ("detrendingSettings", DetrendingSettingsCType),
        ("filteringSettings", FilteringSettingsCType),
        ("windowSettings", WindowSettingsCType)
    ]

class FourierTransformCType(Structure):
    _fields_ = [
        ("len", c_int),
        ("spectrum_real", POINTER(c_double)),
        ("spectrum_imaginary", POINTER(c_double)),
        ("frequencies", POINTER(c_double)),
        ("magnitudes", POINTER(c_double)),
        ("phases", POINTER(c_double))
    ]
    
class ChannelListCType(Structure):
    _fields_ = [
        ("numChannels",c_int),
        ("indices", POINTER(c_int)),
        ("labels", POINTER(c_char_p)),
        ("numBiasChannels",c_int),
        ("biasIndices",POINTER(c_int))
    ]
    
