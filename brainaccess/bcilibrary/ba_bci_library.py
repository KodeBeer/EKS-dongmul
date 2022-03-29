from ctypes import *
from ctypes.util import find_library
from sys import exit

dll_name = 'BABCILibrary.dll'     # is expected to be in PATH
ba_bci_library = None

def get_bci_library():
    global ba_bci_library
    if not ba_bci_library is None:
        return ba_bci_library

    try:
        ba_bci_library = CDLL(find_library(dll_name))
    except OSError:
        print("Could not load {0}".format(dll_name))
        print("Try reinstalling BrainAccess.")
        exit()

    return ba_bci_library