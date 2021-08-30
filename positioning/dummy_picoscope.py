import numpy as np

def Picoscope(filename: str, *args, **kwargs):
    extn = filename[filename.rfind('.'):]
    if extn == '.csv':
        return _Picoscope(filename, *args, **kwargs)
    if extn == '.nps':
        from positioning.file_helper import ChunkedNPStackReader
        return ChunkedNPStackReader(filename, *args, **kwargs) 

class _Picoscope:
    def __init__(self, filename='./data/fishhook_moving_one/store_channeldata_PositionStep_0.csv'):
        print("Initiating Dummy Picoscope")
        self.initialized = False
        self.filename = filename
        self.channel_range = 7

    def __enter__(self):
        print("Opening CSV Files")
        self.connected = True
        return self

    def stream(self):
        arr = np.loadtxt(self.filename, skiprows=1, delimiter=',')
        return arr  # [ch.reshape((-1,)) for ch in np.hsplit(arr, arr.shape[1])]

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing Picoscope")