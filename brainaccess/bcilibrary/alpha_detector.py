from ctypes import *
from brainaccess.bcilibrary import ba_bci_library
from brainaccess.utilities import *

ba_bci_library = ba_bci_library.get_bci_library()

# API

ba_bci_library.baBCILibrary_initializeMotionClassifier.restype = c_int
def initialize(channel_indices):
    """
    Initializes Alpha Detector's internal structures, intializes BrainAccess Core library and attempts to connect to BrainAccess EEG hardware.	

    Must be called before other Alpha Detector functions.
        
    Args:
        ``channel_indices`` ( **list[int]** ): indices of channels that should be used by the algorithm (we recommend using channels placed in occipital region).
        Maximum allowed number of channels is 3.
        
    Returns:
        ``bool``: True on success, False on error.
    """

    ch_ptr = python_array_to_ctype(channel_indices, c_int)

    if ba_bci_library.baBCILibrary_initializeAlphaDetector(ch_ptr, len(channel_indices)) != 0:
        print("Alpha Detector could not be initialized")
        return False

    return True

ba_bci_library.baBCILibrary_startAlphaDetector.restype = c_int
def start():
    """
        Starts EEG data collection.

        Should be called before :meth:`brainaccess.bcilibrary.alpha_detector.predict` or :meth:`brainaccess.bcilibrary.alpha_detector.predict_from_now`.

    Returns:
        ``bool``: True on success, False on error.
    """
    return ba_bci_library.baBCILibrary_startAlphaDetector() == 0

ba_bci_library.baBCILibrary_stopAlphaDetector.restype = c_int
def stop():
    """
        Stops EEG data collection

        Should be called when Alpha Detector is no longer needed.

    Returns:
        ``bool``: True on success, False on error.
    """
    return ba_bci_library.baBCILibrary_stopAlphaDetector() == 0

ba_bci_library.baBCILibrary_estimateAlphaFrequency.restype = c_int
def estimate_alpha():
    """
    Estimates the alpha frequency for the user.

    Each person has a slightly different alpha brainwave frequency, although it is usually in the range of 8-12Hz.
    This algorithm works best by firstly estimating the frequency for the current user.
    When this method is called, user should sit still, with his/her eyes closed for 3 seconds.

    Returns:
        ``bool``: True on success, False on error.
    """
    return ba_bci_library.baBCILibrary_estimateAlphaFrequency() == 0

ba_bci_library.baBCILibrary_predictAlpha.restype = c_double
def predict():
    """
    Predicts alpha wave intensity from the latest EEG data.

    The data used in the previous predictions is reused if needed.
    If not enough data is available, this function firstly waits for the data and only then predicts.  

    Returns:
        ``float``: Estimation of alpha wave intensity as a measure between 0 and 1.    
        For small alpha wave activities expect the value to be around 0.05   
        For strong alpha waves expect the value to be up to 0.5  (larger values are less common).
    """
    return ba_bci_library.baBCILibrary_predictAlpha()

ba_bci_library.baBCILibrary_predictAlphaFromNow.restype = c_double
def predict_from_now():
    """
    Predicts alpha wave intensity from EEG data collected from the moment this function is called.

    Previously collected data is discarded and the algorithm collects the required number of measurements before predicting.
    This can be useful if prediction should be made with data collected after some kind of event.

    Returns:
        ``float``: The same alpha intensity evaluation as :meth:`brainaccess.bcilibrary.alpha_detector.predict`.
    """
    return ba_bci_library.baBCILibrary_predictAlphaFromNow()
