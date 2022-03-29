import numpy as np

def python_array_to_ctype(arr, ctype):
    arrlen = len(arr)
    carr = (ctype* arrlen)()
    for i in range(arrlen):
        carr[i] = arr[i]

    return carr

def egg_data_stream_to_py(eeg_data_stream, samplesCType):    
    eeg_data_stream.num_samples = samplesCType.numSamples
    eeg_data_stream.stream_disrupted = bool(samplesCType.streamDisrupted)
    eeg_data_stream.reading_is_too_slow = bool(samplesCType.readingIsTooSlow)
    eeg_data_stream.connection_lost = bool(samplesCType.connectionLost)
    num_channels = samplesCType.numChannels
    
    acc_data_carray = samplesCType.accelerometerData[:eeg_data_stream.num_samples]
    acc = [[actype.x, actype.y, actype.z] for actype in acc_data_carray]
    eeg_data_stream.accelerometer_data = np.array(acc).T
    
    eeg_data_stream.measurements = np.zeros((num_channels, eeg_data_stream.num_samples))
    eeg_data_stream.lead_status = np.zeros((num_channels, eeg_data_stream.num_samples), dtype=np.int)
    for c in range(num_channels):
        for n in range(eeg_data_stream.num_samples):
            eeg_data_stream.measurements[c][n]=samplesCType.measurements[c][n]
            eeg_data_stream.lead_status[c][n]=samplesCType.leadStatus[c][n]