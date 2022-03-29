from ctypes import *
from brainaccess.bcilibrary import ba_bci_library
from brainaccess.utilities import *    

bci_library = ba_bci_library.get_bci_library()

# API
bci_library.baBCILibrary_initializeSSVEPDetector.restype = c_int
def initialize(channel_indices, ssvep_frequencies):
    """
    Initializes SSVEP Detector's internal structures, intializes BrainAccess Core library and attempts to connect to BrainAccess EEG hardware.

    Args:
        ``channel_indices`` (**list[int]**): indices of channels that should be used by the algorithm. Electrodes should be placed in oxipital region (we suggest O1, O2, Oz).

        ``ssvep_frequencies`` (**list[float]**): flicker frequencies that are provided as visual stimuli for the user.
        For best results, frequencies should be roughly in 8 - 15Hz range and distance between them should be at least 1Hz.
        Each frequency is associated with a class that the algorithm later predicts.

    Returns:
        ``bool``: True if successful, False on error.
    """
    ch_ptr = python_array_to_ctype(channel_indices, c_int)
    ssvep_ptr = python_array_to_ctype(ssvep_frequencies, c_double)

    if bci_library.baBCILibrary_initializeSSVEPDetector(ch_ptr, len(channel_indices), ssvep_ptr, len(ssvep_frequencies)) != 0:
        print("SSVEP Detector could not be initialized")
        return False

    return True

bci_library.baBCILibrary_startSSVEPDetector.restype = c_int
def start():
    """
    Starts EEG data collection

    Should be called before :meth:`brainaccess.sdk.ssvep_detector.predict`

    Returns:
        ``bool``: True if successful, False on error.
    """
    return bci_library.baBCILibrary_startSSVEPDetector() == 0

bci_library.baBCILibrary_stopSSVEPDetector.restype = c_int
def stop():
    """
    Stop EEG data collection

    Should be called when SSVEP Detector is no longer needed.

    Returns:
        ``bool``: True if successful, False on error.
    """
    return bci_library.baBCILibrary_stopSSVEPDetector() == 0

bci_library.baBCILibrary_predictSSVEP.restype = c_int
def predict():
    """
    Predicts class (frequency) on which user is concentrated.	

    Note that EEG data does not instantly reflect the flicker frequencies once the user switches focus to it.
    Rather, it takes a few seconds for it to happen.

    Returns:
        ``int``: Predicted class index or -1 if an error occured.
        Class indices correspond to frequencies provided in :meth:`brainaccess.sdk.ssvep_detector.initialize` (using the same ordering as was provided). 
    """
    return bci_library.baBCILibrary_predictSSVEP()


