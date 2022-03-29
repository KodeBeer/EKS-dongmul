import numpy as np
from ctypes import *
from ctypes.util import find_library
from brainaccess.utilities import *
from brainaccess.ba_ctypes import *
from brainaccess.models import *
from sys import exit

dll_name = 'BACore.dll'     # is expected to be in PATH

try:
    ba_core = CDLL(find_library(dll_name))
except OSError as e:
    print("Could not load " + dll_name)
    print("Try reinstalling BrainAccess Viewer.")
    exit()

# define return type for functions
# acquisition
ba_core.baCore_getData.restype = EEGSamplesCType
ba_core.baCore_getDataFromNow.restype = EEGSamplesCType
ba_core.baCore_getDataSamples.restype = EEGSamplesCType
ba_core.baCore_getDataSamplesFromNow.restype = EEGSamplesCType
ba_core.baCore_getCurrentData.restype = EEGSamplesCType
ba_core.baCore_initialize.restype = c_int
ba_core.baCore_loadConfig.restype = c_int
ba_core.baCore_setChannels.restype = c_int
ba_core.baCore_setSamplingFrequency.restype = c_double
ba_core.baCore_getNumChannels.restype = c_int
ba_core.baCore_getSamplingFrequency.restype = c_double
ba_core.baCore_getActiveChannels.restype = ChannelListCType
ba_core.baCore_batteryLevel.restype = c_int
ba_core.baCore_isChargingOn.restype = c_int
ba_core.baCore_batteryVoltage.restype = c_int
ba_core.baCore_hasConnection.restype = c_int

# preprocessing:
ba_core.baCore_saveData.restype = c_int
ba_core.baCore_loadData.restype = DataDescriptionCType
ba_core.baCore_estimateSignalQuality.restype = c_double
ba_core.baCore_preprocess.restype = POINTER(c_double)
ba_core.baCore_fourierTransform.restype = FourierTransformCType
ba_core.baCore_getPreprocessingSettings.restype = PreprocessingSettingsCType

# API


def save_data(eeg_data, file_path, separator=' '):
    """Saves data to a csv file.
        
    Args:
        ``eeg_data`` ( :class:`brainaccess.models.EEGData` ): an object containing EEG data and information on the file.  
        
        ``file_path`` (**string**):  full path including the file name. Escaped back slashes ("\\\ \\\ ") or forward slashes ("/") should be used.
        
        ``separator`` (**char**):  a separator character used to separate columns in the csv file.
        
    Returns:
        int: True if the data was successfully saved, False if I/O error occured.
    """

    num_channels = len(eeg_data.labels)
    num_samples = len(eeg_data.measurements[0])
    csettings = DataDescriptionCType()
    csettings.filePath = c_char_p(file_path.encode('utf-8'))
    csettings.separator = c_char(separator.encode('utf-8'))
    csettings.numChannels = c_int(num_channels)
    csettings.numSamples = c_int(num_samples)

    en_labels = [l.encode('utf-8') for l in eeg_data.labels]
    csettings.labels = python_array_to_ctype(en_labels, c_char_p)
    
    c_double_p = POINTER(c_double)
    c_double_pp = POINTER(c_double_p)
    carr=np.ctypeslib.as_ctypes(eeg_data.measurements)
    c_double_p_arr = c_double_p * carr._length_
    csettings.measurements = cast(c_double_p_arr(*(cast(row,c_double_p) for row in carr)),c_double_pp)
        
    acc = []
    for n in range(num_samples):
        accsettings = AccelerometerDataCType()
        accsettings.x = c_double(eeg_data.accelerometer_data[0][n])
        accsettings.y = c_double(eeg_data.accelerometer_data[1][n])
        accsettings.z = c_double(eeg_data.accelerometer_data[2][n])
        acc.append(accsettings)

    csettings.accelerometerData = python_array_to_ctype(
        acc, AccelerometerDataCType)

    csettings.samplingFrequency = c_double(eeg_data.sampling_frequency)

    res = ba_core.baCore_saveData(csettings)

    return res == 0


def load_data(file_path, separator=' '):
    """Loads data from a csv file.
    
    Args:
        ``file_path`` (**string**): a full path including the file name. Escaped back slashes ("\\\ \\\ ") or forward slashes ("/") should be used.

        ``separator`` (**char**): a separator character used to separate columns in the csv file.
    
    Returns:
        :class:`brainaccess.models.EEGData`: an object containing EEG data, accelerometer data and other relevant info. Returns empty EEG and accelerometer data arrays (see object attributes) if loading was unsuccessful.
        
    """
    csettings = ba_core.baCore_loadData(
        c_char_p(file_path.encode('utf-8')), c_char(separator.encode('utf-8')))

    e = EEGData()
    num_channels = csettings.numChannels
    num_samples = csettings.numSamples
    if num_channels > 0 and num_samples > 0:
        e.sampling_frequency = csettings.samplingFrequency
        temp = csettings.labels[:num_channels]
        for label in temp:
            e.labels.append(label.decode("utf-8"))

        acc = [[s.x, s.y, s.z] for s in csettings.accelerometerData[:num_samples]]

        e.accelerometer_data = np.array(acc).T

        e.measurements = np.zeros((num_channels, num_samples))
        for c in range(num_channels):
            for n in range(num_samples):
                e.measurements[c][n] = csettings.measurements[c][n]

    return e


def configure_logging(verbosity, output_file):
    """Configures BrainAccess Core library logging.
    
    Args:
        verbocity (**int**): a value between 0 and 4, which describes what information is logged.  
            | 0 -- nothing is logged,
            | 1 -- only error messages are logged,
            | 2 -- warnings and error messages,
            | 3 -- information messages designed to briefly reflect the library status + everything above,
            | 4 -- debug messages, thoroughly describing actions performed by the library + everything above.
        
        output_file (**string**): might be either an empty string, a full path or the name of the log output file.  
            | If outputFile is an empty string, logging will be done to console.  
            | If the output file name is provided without the full path, the file is created in the libarary's directory.  
            | If the output file already exists, log output is appended to the existing file.
            | Escaped back slashes ("\\\ \\\ ") or forward slashes ("/") should be used.
    """

    ba_core.baCore_configureLogging(
        c_int(verbosity), c_char_p(output_file.encode('utf-8')))


def has_connection():
    """Checks if BrainAccess core library still has connection with BrainAccess EEG hardware.
    
    Requires initialization.

    Returns:
        ``bool``: True if library can communicate, False if connection is broken.
    """
    res = ba_core.baCore_hasConnection()
    return bool(res)


def set_buffer_size(buffer_size):
    """Sets the size of internal buffer used in acquisition.

    Requires initialization.
    
    Args:
        ``buffer_size`` (**int**): buffer length (min 1, max 400000), the maximum number of samples that could be stored in the internal buffer.
    """
    ba_core.baCore_setBufferSize(c_int(buffer_size))


def start_acquisition():
    """Starts acquiring data from BrainAccess EEG hardware and filling an internal buffer of BrainAccess Core library.
    
       Requires initialization.
    """
    ba_core.baCore_startAcquisition()


def stop_acquisition():
    """Stops acquiring data from BrainAccess EEG hardware.
    
       Requires initialization.
    """
    ba_core.baCore_stopAcquisition()


def discard_data():
    """Discards data in the internal buffer of baCore.
    
       Requires initialization.
    """
    ba_core.baCore_discardData()


def set_channel_labels(indices, labels):
    """Updates the labels for certain channels.

    Requires initialization.
    
    Args:
        ``indices`` (**list[int]**): A list of channel numbers for which the labels should be updated.

        ``labels`` (**list[string]**): A list of labels corresponding to the indices. A label might be an empty string, meaning that the label needs to be removed.
    """
    cindices = python_array_to_ctype(indices, c_int)
    nlabels = len(indices)
    en_labels = [l.encode('utf-8') for l in labels]
    clabels = python_array_to_ctype(en_labels, c_char_p)
    ba_core.baCore_setChannelLabels(cindices, clabels, nlabels)


def initialize():
    """Initializes BrainAccess Core library and attempts to connect to BrainAccess EEG hardware.\n
    initialize or load_config need to be called before any further actions,
    that require connection to the BrainAccess EEG hardware, are done.
    
    Returns:
        int: 
            | 0 if successful,
            | 1 if connection could not be established due to WiFi issues, 
            | 2 if no board is inserted in the first board slot, 
            | 3 if called when acquisition is in progress which is not allowed.
    """
    res = ba_core.baCore_initialize()
    return res


def load_config(config_path):
    """Loads a configuration file with acquisition parameters from the provided path and (re)initializes the library.

    When ba_core.load_config is used, ba_core.intialize is not necessary beforehand.
    
    Args:
        ``config_path`` (**string**): a full path including the configuration file name. Escaped back slashes ("\\\ \\\ ") or forward slashes ("/") should be used.
        
    Returns:
        ``int``: 
            | 0 if successful,
            | 1 if connection could not be established due to WiFi issues, 
            | 2 if no board is inserted in the first board slot, 
            | 3 if called when acquisition is in progress which is not allowed.
    """
    return ba_core.baCore_loadConfig(c_char_p(config_path.encode('utf-8')))


def save_config(config_path):
    """Saves current acquisition parameters to configuration file.\n
    This is only needed when it is wished to have multiple configurations ready for different experiments.
    Otherwise, all the values set using this API are automatically saved to the library's working directory.
    
    Args:
        ``config_path`` (**string**): a full path including the configuration file name OR an empty string. If an empty string is provided, the configuration will be saved to the same location it was loaded from. If the full path is provided, escaped back slashes ("\\\ \\\ ") or forward slashes ("/") should be used.
    """
    ba_core.baCore_saveConfig(c_char_p(config_path.encode('utf-8')))


def get_num_available_channels():
    """Gets the number of available channels in connected BrainAccess EEG hardware.
    
    Requires initialization.

    Returns:
        ``int``: number of channels.
    """
    return ba_core.baCore_getNumChannels()


def get_data_samples(num_samples):
    """Requests a number of data samples. These are pulled from internal buffer or 
    acquired from the hardware if data in the buffer is not sufficient.
    This function should be used for continuous acquisition.

    Requires initialization and active acquisition.
    
    Args:
        ``num_samples`` (**int**): number of samples to acquire.
        
    Returns:
        :class:`brainaccess.models.EEGDataStream`: an object that holds info on hardware status, EEG data, lead status and accelerometer data.
    """
    samplesCType = ba_core.baCore_getDataSamples(c_int(num_samples))
    eeg_samples = EEGDataStream()
    egg_data_stream_to_py(eeg_samples, samplesCType)
    return eeg_samples


def get_data_samples_from_now(num_samples):
    """Requests a number of data samples to acquire straightaway by BrainAccess EEG hardware. 
    This function should be used for triggered acquisition.

    Requires initialization and active acquisition.
    
    Args:
        ``num_samples`` (**int**): number of samples to acquire.
        
    Returns:
        :class:`brainaccess.models.EEGDataStream`: an object that holds info on hardware status, EEG data, lead status and accelerometer data.
    """
    samplesCType = ba_core.baCore_getDataSamplesFromNow(c_int(num_samples))
    eeg_samples = EEGDataStream()
    egg_data_stream_to_py(eeg_samples, samplesCType)
    return eeg_samples


def get_data(time_span_in_milliseconds):
    """Requests data acquired (or acquire if not yet acquired) by BrainAccess EEG hardware. 
    This function should be used for continuous acquisition.

    Requires initialization and active acquisition.
    
    Args:
        ``time_span_in_milliseconds`` (**int**): recording length to acquire in milliseconds.
        
    Returns:
        :class:`brainaccess.models.EEGDataStream`: an object that holds info on hardware status, EEG data, lead status and accelerometer data.
    """
    samplesCType = ba_core.baCore_getData(c_int(time_span_in_milliseconds))
    eeg_samples = EEGDataStream()
    egg_data_stream_to_py(eeg_samples, samplesCType)
    return eeg_samples


def get_data_from_now(time_span_in_milliseconds):
    """Requests data to acquire straightaway by BrainAccess EEG hardware. 
    This function should be used for triggered acquisition.

    Previously collected data is discarded.

    Requires initialization and active acquisition.
    
    Args:
        ``time_span_in_milliseconds`` (**int**): recording length to acquire in milliseconds.
        
    Returns:
        :class:`brainaccess.models.EEGDataStream`: an object that holds info on hardware status, EEG data, lead status and accelerometer data.
    """
    samplesCType = ba_core.baCore_getDataFromNow(
        c_int(time_span_in_milliseconds))
    eeg_samples = EEGDataStream()
    egg_data_stream_to_py(eeg_samples, samplesCType)
    return eeg_samples


def get_current_data():
    """Requests all the data that is currently acquired by BrainAccess EEG hardware.     

    The number of samples returned will be different, depending on the time passed since the last call.
    For continuous acquisition we recommend using :meth:`brainaccess.core.get_data` or :meth:`brainaccess.core.get_data_samples`

    Requires initialization and active acquisition.
        
    Returns:
        :class:`brainaccess.models.EEGDataStream`: an object that holds info on hardware status, EEG data, lead status and accelerometer data.
    """
    samplesCType = ba_core.baCore_getCurrentData()
    eeg_samples = EEGDataStream()
    egg_data_stream_to_py(eeg_samples, samplesCType)
    return eeg_samples


def get_active_channels():
    """Gets a list of channels that are turned on in BrainAccess EEG hardware.

    Requires initialization.
    
    Returns:
        Tuple (activeChannels, biasChannels, labels)
            | where
            | ``activeChannels`` is a list of channel indices turned on in hardware,
            | ``biasChannels`` is a list of channel indices used in bias feedback
            | ``labels`` is a list of string labels of the active channels.
    """
    settingsCType = ba_core.baCore_getActiveChannels()
    channel_idx = settingsCType.indices[:settingsCType.numChannels]
    bias_channel_idx = settingsCType.biasIndices[:settingsCType.numBiasChannels]
    labels = [label.decode("utf-8")
              for label in settingsCType.labels[:settingsCType.numChannels]]

    return channel_idx, bias_channel_idx, labels


def set_channels(channel_idx, bias_channel_idx):
    """Turns on the specified channels in BrainAccess EEG hardware

    Requires initialization and inactive acquisition.
    
    Args:
        ``channel_idx`` (**list[int]**): a list containing channel numbers to turn on.
        BrainAccess Core always handles and holds channel indices in ascending order based on index integer value.
        This includes acquisition data (obtained from baCore_getData() methods) which is always provided in the ascending order of channel indices.
        We recommend users to have indices in ascending order in their code as well, in order to prevent confusion and mishaps.

        ``bias_channel_idx`` (**list[int]**): a list containing channel numbers that should be used in bias feedback.
        Similarly to channelIdx, we recommend providing indices in ascending order.
    
    Returns:
        int: 
            | 0 if succesful, 
            | 3 if channel set was attempted during acquisition in progress (not allowed), 
            | 4 if library was not (successfully) initialized.
    """

    channelIdx = python_array_to_ctype(channel_idx, c_int)
    channelIdxLen = c_int(len(channel_idx))
    biasChannelIdx = python_array_to_ctype(bias_channel_idx, c_int)
    biasChannelIdxLen = c_int(len(bias_channel_idx))

    res = ba_core.baCore_setChannels(
        channelIdx, channelIdxLen, biasChannelIdx, biasChannelIdxLen)
    return res


def get_sampling_frequency():
    """Gets the sampling frequency currently used by BrainAccess EEG hardware.
    
    Returns:
        ``double``: sampling frequency in Hz.
    """
    res = ba_core.baCore_getSamplingFrequency()
    return res


def set_sampling_frequency(sampling_frequency):
    """Sets the sampling frequency for the BrainAccess EEG hardware.
    
    Args:
        ``sampling_frequency`` (**double**): sampling frequency in Hz. It can either be 250.0 Hz or 125.0 Hz.
        
    Returns:
        ``double``: The actual frequency that has been set in the hardware in Hz.
    """
    return ba_core.baCore_setSamplingFrequency(c_double(sampling_frequency))


def get_battery_level():
    """Gets battery charge level. It is a rough estimate determined from the battery voltage.
    
    Requires initialization.

    Returns:
        ``int``: battery level in percentage 
    """
    return ba_core.baCore_batteryLevel()


def get_battery_voltage():
    """Gets voltage of the integrated LiPo battery.
    
    Requires initialization.

    Returns:
        ``int``: battery voltage in mV. Approximately, 4200mV for fully charged battery and 3600mV for fully depleted.
    """
    return ba_core.baCore_batteryVoltage()


def is_charging_on():
    """Gets battery charging status.

    Requires initialization.
    
    Returns:
        ``bool``: True if battery charger is plugged in, False otherwise.
    """
    res = ba_core.baCore_isChargingOn()
    return bool(res)


def load_preprocessing_config(config_path):
    """Loads configuration file with signal preprocessing parameters.
    
    If the configuration is loaded successfully, it is saved to the library's working directory and 
    automatically reloaded on successive library runs.

    Args:
        ``config_path`` (**string**): a full path including the configuration file name. Escaped back slashes ("\\\ \\\ ") or forward slashes ("/") should be used.
    """

    ba_core.baCore_loadPreprocessingConfig(
        c_char_p(config_path.encode('utf-8')))


def save_preprocessing_config(config_path):
    """Saves signal preprocessing parameters to a configuration file.
    
    Args:
        ``config_path`` (**string**): a full path including the configuration file name OR an empty string. If a full path is provided, escaped back slashes ("\\\ \\\ ") or forward slashes ("/") should be used. If an empty string is provided, configuration will be saved to the same location it was loaded from.
    """
    ba_core.baCore_savePreprocessingConfig(
        c_char_p(config_path.encode('utf-8')))


def estimate_quality(signal):
    """Estimates EEG signal quality.
    
    Args:
        ``signal`` ( **list[float]** OR **numpy array [float64]**): 1D array containing an EEG signal. The signal should be detrended before supplying it to this function.
        
    Returns:
        double: a number in range 0-1, 1 for good quality, 0 for worst quality
    """
    arr = python_array_to_ctype(signal, c_double)
    return ba_core.baCore_estimateSignalQuality(arr, c_int(len(signal)))


def fourier_transform(signal):
    """Calculates FFT for a given signal.
    
    Args:
        ``signal`` ( **list[float]** OR **numpy array [float64]** ): 1D array containing an EEG signal.
        
    Returns:
        :class:`brainaccess.models.FourierTransform`: an object that holds the results of FFT.
    """
    arrlen = len(signal)

    arr = python_array_to_ctype(signal, c_double)

    ftCType = ba_core.baCore_fourierTransform(arr, c_int(arrlen))

    fourier_transform = FourierTransform()
    fourier_transform.frequencies = np.array(ftCType.frequencies[:ftCType.len])
    fourier_transform.spectrum = np.array(
        ftCType.spectrum_real[:ftCType.len])+1j*np.array(ftCType.spectrum_imaginary[:ftCType.len])
    fourier_transform.magnitudes = np.array(ftCType.magnitudes[:ftCType.len])
    fourier_transform.phases = np.array(ftCType.phases[:ftCType.len])

    return fourier_transform


def set_preprocessing_sampling_frequency(sampling_frequency):
    """Sets sampling frequency for preprocessing functions.
    
    Args:
        ``sampling_frequency`` (**double**): sampling frequency in Hz.
    """
    ba_core.baCore_setPreprocessingSamplingFrequency(
        c_double(sampling_frequency))


def set_detrend_settings(detrend_settings):
    """Sets parameters for signal detrending algorithm.
    
    Args:
        ``detrend_settings`` (:class:`brainaccess.models.DetrendSettings`): an object holding parameters for detrend algorithm.
    """
    csettings = DetrendingSettingsCType()
    csettings.isActive = c_int(1 if detrend_settings.is_active else 0)
    csettings.polynomialDegree = c_int(detrend_settings.polynomial_degree)

    ba_core.baCore_configureDetrending(csettings)


def set_filter_settings(filters):
    """Sets filters for signal filtering.
    
    Args:
        ``filters`` ( **list** [:class:`brainaccess.models.FilterSettings`] ): a list of filters, where each filter is an object containing filter parameters.
    """
    csettings = FilteringSettingsCType()
    csettings.numFilters = c_int(len(filters))
    cfilts = []
    if len(filters) > 0:
        for filt in filters:
            c = SingleFilterSettingsCType()
            c.isActive = c_int(1 if filt.is_active else 0)
            ltype = filt.type.lower()
            if (ltype == "bandpass"):
                c.type = 0
            elif (ltype == "bandstop"):
                c.type = 1
            elif (ltype == "lowpass"):
                c.type = 2
            elif (ltype == "highpass"):
                c.type = 3
            else:
                print("Unknown Filter Type: " + ltype+". Using bandpass.")
                c.type = 0

            c.order = c_int(filt.order)
            c.minFrequency = c_double(filt.min_frequency)
            c.maxFrequency = c_double(filt.max_frequency)

            cfilts.append(c)

        csettings.filters = python_array_to_ctype(
            cfilts, SingleFilterSettingsCType)

    ba_core.baCore_configureFiltering(csettings)


def set_window_settings(window_settings):
    """Sets parameters for temporal window.
    
    Args:
        ``window_settings`` (:class:`brainaccess.models.WindowSettings`): an object holding parameters for temporal window.
    """

    c = WindowSettingsCType()
    c.isActive = c_int(1 if window_settings.is_active else 0)
    ltype = window_settings.type.lower()
    if (ltype == "tukey"):
        c.type = 0
    elif (ltype == "hann"):
        c.type = 1
    else:
        print("Unknown window type: " + ltype+'. Using tukey window.')
        c.type = 0

    c.tukeyAlpha = c_double(window_settings.tukey_alpha)

    ba_core.baCore_configureWindowFunction(c)


def set_preprocessing_settings(fs, detrend_settings=None, filters=[], window_settings=None):
    """Sets parameters for signal preprocessing.
    
    Args:
        ``fs`` (**float**): sampling frequency in Hz,

        ``detrend_settings`` (:class:`brainaccess.models.DetrendSettings`): an object holding parameters for detrend algorithm.

        ``filters`` ( **list** [:class:`brainaccess.models.FilterSettings`] ): a list of filters, where each filter is an object containing filter parameters.

        ``window_settings`` (:class:`brainaccess.models.WindowSettings`): an object holding temporal window parameters.
    """
    csettings = PreprocessingSettingsCType()

    csettings.samplingFrequency = c_double(fs)

    csettings.detrendingSettings = DetrendingSettingsCType()
    csettings.detrendingSettings.isActive = False
    if not detrend_settings is None:
        csettings.detrendingSettings.isActive = c_int(
            1 if detrend_settings.is_active else 0)
        csettings.detrendingSettings.polynomialDegree = c_int(
            detrend_settings.polynomial_degree)

    cfsettings = FilteringSettingsCType()
    cfsettings.numFilters = 0
    cfilts = []
    if not filters is None and len(filters) > 0:
        cfsettings.numFilters = c_int(len(filters))
        for filt in filters:
            c = SingleFilterSettingsCType()
            c.isActive = c_int(1 if filt.is_active else 0)
            ltype = filt.type.lower()
            if (ltype == "bandpass"):
                c.type = 0
            elif (ltype == "bandstop"):
                c.type = 1
            elif (ltype == "lowpass"):
                c.type = 2
            elif (ltype == "highpass"):
                c.type = 3
            else:
                print("Unknown Filter Type: " + ltype+". Using bandpass.")
                c.type = 0

            c.order = c_int(filt.order)
            c.minFrequency = c_double(filt.min_frequency)
            c.maxFrequency = c_double(filt.max_frequency)

            cfilts.append(c)

        cfsettings.filters = python_array_to_ctype(cfilts, SingleFilterSettingsCType)

    csettings.filteringSettings = cfsettings

    csettings.windowSettings = WindowSettingsCType()
    csettings.windowSettings.isActive = False
    csettings.windowSettings.tukeyAlpha = 0.2
    if not window_settings is None:
        csettings.windowSettings.isActive = c_int(
            1 if window_settings.is_active else 0)
        ltype = window_settings.type.lower()
        if (ltype == "tukey"):
            csettings.windowSettings.type = 0
        elif (ltype == "hann"):
            csettings.windowSettings.type = 1
        else:
            print("Unknown window type: " + ltype+'. Using tukey window.')
            csettings.windowSettings.type = 0

        csettings.windowSettings.tukeyAlpha = c_double(window_settings.tukey_alpha)

    ba_core.baCore_configurePreprocessing(csettings)


def get_preprocessing_settings():
    """Gets the current parameters for signal processing.
    
    Returns:
        ``Tuple`` (**int**, :class:`brainaccess.models.DetrendSettings`, **list** [:class:`brainaccess.models.FilterSettings`], :class:`brainaccess.models.WindowSettings` )

        where the first Tuple element is the sampling frequency.
    """

    csettings = ba_core.baCore_getPreprocessingSettings()

    fs = csettings.samplingFrequency

    detrend_settings = DetrendSettings()
    detrend_settings.is_active = bool(csettings.detrendingSettings.isActive)
    detrend_settings.polynomial_degree = csettings.detrendingSettings.polynomialDegree

    filters = []
    for cfilt in csettings.filteringSettings.filters[:csettings.filteringSettings.numFilters]:
        f = FilterSettings()
        f.is_active = bool(cfilt.isActive)

        if (cfilt.type == 0):
            f.type = "bandpass"
        elif (cfilt.type == 1):
            f.type = "bandstop"
        elif (cfilt.type == 2):
            f.type = "lowpass"
        elif (cfilt.type == 3):
            f.type = "highpass"

        f.order = cfilt.order
        f.min_frequency = cfilt.minFrequency
        f.max_frequency = cfilt.maxFrequency

        filters.append(f)

    window_settings = WindowSettings()
    window_settings.is_active = bool(csettings.windowSettings.isActive)

    if (csettings.windowSettings.type == 0):
        window_settings.type = 'tukey'

    elif (csettings.windowSettings.type == 1):
        window_settings.type = 'hann'

    window_settings.tukey_alpha = csettings.windowSettings.tukeyAlpha

    return fs, detrend_settings, filters, window_settings


def preprocess(signal):
    """Processes an EEG signal with given preprocessing parameters.
    
    Args:
        ``signal`` (**list[float]** OR **numpy array [float64]**): 1D array containing an EEG signal
        
    Returns:
        ``numpy array [float64]``: processed signal.
    """
    npoints = len(signal)

    arr = python_array_to_ctype(signal, c_double)
    pntr = ba_core.baCore_preprocess(arr, c_int(npoints))

    processed_signal = np.array(pntr[:npoints])

    return processed_signal
