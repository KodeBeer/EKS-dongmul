from ctypes import *
from brainaccess.bcilibrary import ba_bci_library
    

bci_library = ba_bci_library.get_bci_library()
classes = ["calm", "blink", "double_blink", "teeth", "eyes_up", "eyes_down"]

# API

bci_library.baBCILibrary_initializeMotionClassifier.restype = c_int
def initialize(fp1Idx, fp2Idx):
    """
    Initializes Motion Classifier's internal structures, intializes BrainAccess Core library and attempts to connect to BrainAccess EEG hardware.

    Note that only Fp1 and Fp2 channels are suitable for this algorithm.

    Args:
        ``fp1Idx`` (**int**): index of the channel that is in the Fp1 position.

        ``fp2Idx`` (**int**): index of the channel that is in the Fp2 position.

    Returns:
        ``bool``: True on success, False on error.
    """
    if bci_library.baBCILibrary_initializeMotionClassifier(fp1Idx, fp2Idx) != 0:
        print("MotionClassifier could not be initialized")
        return False

    return True

def start():
    """
        Starts EEG data collection.

        Should be called before :meth:`brainaccess.sdk.motion_classifier.predict`

    Returns:
        ``bool``: True on success, False on error.
    """
    bci_library.baBCILibrary_startMotionClassifier()

def stop():
    """
        Stops EEG data collection

        Should be called when Motion Classifier is no longer needed.

    Returns:
        ``bool``: True on success, False on error.
    """
    bci_library.baBCILibrary_stopMotionClassifier()

bci_library.baBCILibrary_predictMotionClassifier.restype = POINTER(c_double)

def predict():
    '''
    Predicts which motion was performed by the user

    The prediction is made from the last 2.5 seconds of data.
    If not enough data is available for a prediction, this function waits for the required data
    and only then predicts.

    When calling :meth:`brainaccess.sdk.motion_classifier.predict` consequently, the previously collected data is reused,
    meaning that predictions can be made as often as needed.

    Note that the accuracy of the algorithm depends if the collected EEG data captures the whole motion.
    This means that if Motion Classifier predicts on data that only has the start of the motion recorded,
    the prediction will not be accurate.

    To counteract this, we suggest predicting often and accepting the prediction as trustworthy only when
    the prediction is the same for some number of times in a row. See Motion Classifier Browser Controller demo
    for an example.

    Returns:
        ``Tuple(list[double], list[string])``:   
            | First item is probabilities that each of the possible motions were performed. Probabilities are given in such order:  
            | Calm (no action was performed), Blink (single blink), Double Blink, Teeth (teeth grind), Eyes Up (quick eye movement upwards), Eyes Down (eye movement downwards).   

            | Second item is the names of the motion classes (always provided in the same order, included just for convenince):  
            | 'calm', 'blink', 'double_blink', 'teeth', 'eyes_up', 'eyes_down'
    '''
    predictions = bci_library.baBCILibrary_predictMotionClassifier()[:6]
    return predictions, classes

def discard_data():
    '''
    Discards currently collected data, data collection continues from scratch.

    This can be useful when a pause between predictions is needed.
    For example, it can be used after the user performs some action and it triggers a response in GUI.
    Then discarding data would allow to remove data that was collected while the user was waiting for the GUI response.
    '''
    bci_library.baBCILibrary_discardMotionClassifierData()


