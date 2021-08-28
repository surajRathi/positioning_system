import ctypes
import time

import numpy as np
import picosdk.functions as pf
from picosdk.errors import PicoSDKCtypesError
from picosdk.ps4000a import ps4000a as ps


class Picoscope:
    def __init__(self, buffer_size=100000):
        print("Initiating Picoscope")
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.connected = False
        self.initialized = False
        self.buffers_initialized = False
        self.buffer_size = int(buffer_size)
        self.channel_range = 7

        self._buffers = {}

        # TODO Enable certain channels

    def _setup_channels(self):
        if not self.connected:
            raise Exception("Picoscope not connected")

        enabled = 1
        # disabled = 0
        analogue_offset = 0.0  # V
        # range = PS4000A_2V = 7
        coupling_type = ps.PS4000A_COUPLING['PS4000A_DC']  # 1

        self.status["setChA"] = ps.ps4000aSetChannel(self.chandle,
                                                     ps.PS4000A_CHANNEL['PS4000A_CHANNEL_A'],  # 0
                                                     enabled,
                                                     coupling_type,  # 1
                                                     self.channel_range,
                                                     analogue_offset)
        pf.assert_pico_ok(self.status["setChA"])

        self.status["setChB"] = ps.ps4000aSetChannel(self.chandle,
                                                     ps.PS4000A_CHANNEL['PS4000A_CHANNEL_B'],  # 1
                                                     enabled,
                                                     coupling_type,  # 1
                                                     self.channel_range,
                                                     analogue_offset)
        pf.assert_pico_ok(self.status["setChB"])

        self.status["setChC"] = ps.ps4000aSetChannel(self.chandle,
                                                     ps.PS4000A_CHANNEL['PS4000A_CHANNEL_C'],  # 2
                                                     enabled,
                                                     coupling_type,
                                                     self.channel_range,
                                                     analogue_offset)
        pf.assert_pico_ok(self.status["setChC"])

        self.status["setChD"] = ps.ps4000aSetChannel(self.chandle,
                                                     ps.PS4000A_CHANNEL['PS4000A_CHANNEL_D'],
                                                     enabled,
                                                     coupling_type,
                                                     self.channel_range,
                                                     analogue_offset)
        pf.assert_pico_ok(self.status["setChD"])

        self.status["setChE"] = ps.ps4000aSetChannel(self.chandle,
                                                     ps.PS4000A_CHANNEL['PS4000A_CHANNEL_E'],
                                                     enabled,
                                                     coupling_type,
                                                     self.channel_range,
                                                     analogue_offset)
        pf.assert_pico_ok(self.status["setChE"])

        self.initialized = True

    def _initialize_buffers(self):
        if not self.initialized:
            raise Exception("Channels not set up")

        self._buffers['A'] = np.zeros(shape=self.buffer_size, dtype=np.int16)
        self._buffers['B'] = np.zeros(shape=self.buffer_size, dtype=np.int16)
        self._buffers['C'] = np.zeros(shape=self.buffer_size, dtype=np.int16)
        self._buffers['D'] = np.zeros(shape=self.buffer_size, dtype=np.int16)
        self._buffers['E'] = np.zeros(shape=self.buffer_size, dtype=np.int16)

        memory_segment = 0

        # Set data buffer location for data collection from channel A
        # handle = chandle
        # source = PS4000A_CHANNEL_A = 0
        # pointer to buffer max = ctypes.byref(self._buffers['A'])
        # pointer to buffer min = ctypes.byref(bufferAMin)
        # buffer length = maxSamples
        # segment index = 0
        # ratio mode = PS4000A_RATIO_MODE_NONE = 0
        self.status["setDataBuffersA"] = ps.ps4000aSetDataBuffers(self.chandle,
                                                                  ps.PS4000A_CHANNEL['PS4000A_CHANNEL_A'],
                                                                  self._buffers['A'].ctypes.data_as(
                                                                      ctypes.POINTER(ctypes.c_int16)),
                                                                  None,
                                                                  self.buffer_size,
                                                                  memory_segment,
                                                                  ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        pf.assert_pico_ok(self.status["setDataBuffersA"])

        self.status["setDataBuffersB"] = ps.ps4000aSetDataBuffers(self.chandle,
                                                                  ps.PS4000A_CHANNEL['PS4000A_CHANNEL_B'],
                                                                  self._buffers['B'].ctypes.data_as(
                                                                      ctypes.POINTER(ctypes.c_int16)),
                                                                  None,
                                                                  self.buffer_size,
                                                                  memory_segment,
                                                                  ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        pf.assert_pico_ok(self.status["setDataBuffersB"])

        self.status["setDataBuffersC"] = ps.ps4000aSetDataBuffers(self.chandle,
                                                                  ps.PS4000A_CHANNEL['PS4000A_CHANNEL_C'],
                                                                  self._buffers['C'].ctypes.data_as(
                                                                      ctypes.POINTER(ctypes.c_int16)),
                                                                  None,
                                                                  self.buffer_size,
                                                                  memory_segment,
                                                                  ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        pf.assert_pico_ok(self.status["setDataBuffersC"])

        self.status["setDataBuffersD"] = ps.ps4000aSetDataBuffers(self.chandle,
                                                                  ps.PS4000A_CHANNEL['PS4000A_CHANNEL_D'],
                                                                  self._buffers['D'].ctypes.data_as(
                                                                      ctypes.POINTER(ctypes.c_int16)),
                                                                  None,
                                                                  self.buffer_size,
                                                                  memory_segment,
                                                                  ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        pf.assert_pico_ok(self.status["setDataBuffersD"])

        self.status["setDataBuffersE"] = ps.ps4000aSetDataBuffers(self.chandle,
                                                                  ps.PS4000A_CHANNEL['PS4000A_CHANNEL_E'],
                                                                  self._buffers['E'].ctypes.data_as(
                                                                      ctypes.POINTER(ctypes.c_int16)),
                                                                  None,
                                                                  self.buffer_size,
                                                                  memory_segment,
                                                                  ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        pf.assert_pico_ok(self.status["setDataBuffersE"])

        self.buffers_initialized = True

    def __enter__(self):
        print("Connecting to Picoscope")

        self.status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(self.chandle), None)
        try:
            pf.assert_pico_ok(self.status["openunit"])
            print('open unit done')
        except PicoSDKCtypesError:
            power_status = self.status["openunit"]
            if power_status == 286:
                self.status["changePowerSource"] = ps.ps4000aChangePowerSource(self.chandle, power_status)
            else:
                raise
            pf.assert_pico_ok(self.status["changePowerSource"])

        self.connected = True
        self._setup_channels()
        self._initialize_buffers()

        return self

    def stream(self, n_samples):
        if not self.buffers_initialized:
            raise Exception("Picoscope not initialized, use a context manager to load it")

        num_buffers_to_receive = int(n_samples // self.buffer_size)
        total_samples = self.buffer_size * num_buffers_to_receive

        # print(f"Getting {total_samples} samples with buffer size {self.buffer_size} for {total_samples // 1e6} seconds and {num_buffers_to_receive} buffers.")

        # Begin streaming mode:
        sample_interval = ctypes.c_int32(1)
        sample_units = ps.PS4000A_TIME_UNITS['PS4000A_US']
        max_pre_trigger_samples = 0  # We are not triggering:
        autoStopOn = 1
        downsample_ratio = 1  # No downsampling:

        self.status["runStreaming"] = ps.ps4000aRunStreaming(self.chandle,
                                                             ctypes.byref(sample_interval),
                                                             sample_units,
                                                             max_pre_trigger_samples,
                                                             total_samples,
                                                             autoStopOn,
                                                             downsample_ratio,
                                                             ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'],
                                                             self.buffer_size)

        pf.assert_pico_ok(self.status["runStreaming"])

        actualSampleInterval = sample_interval.value
        actualSampleIntervalNs = actualSampleInterval * 1000

        # print("Capturing at sample interval %s ns" % actualSampleIntervalNs)

        # Find maximum ADC count value
        # handle = chandle
        # pointer to value = ctypes.byref(maxADC)
        maxADC = ctypes.c_int16()
        self.status["maximumValue"] = ps.ps4000aMaximumValue(self.chandle, ctypes.byref(maxADC))
        pf.assert_pico_ok(self.status["maximumValue"])
        channelInputRanges = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000]
        vRange = channelInputRanges[self.channel_range]

        conversion_factor = vRange / maxADC.value

        # Inline the pf.adc2mV
        def np_adc2mV(arr: np.array) -> np.array:
            return arr * conversion_factor

        # We need a big buffer, not registered with the driver, to keep our complete capture in.
        # TODO: Can't we just store a list / queue of small buffers?
        bufferCompleteA = np.zeros(shape=total_samples, dtype=np.int16)
        bufferCompleteB = np.zeros(shape=total_samples, dtype=np.int16)
        bufferCompleteC = np.zeros(shape=total_samples, dtype=np.int16)
        bufferCompleteD = np.zeros(shape=total_samples, dtype=np.int16)
        bufferCompleteE = np.zeros(shape=total_samples, dtype=np.int16)

        global nextSample, autoStopOuter, wasCalledBack
        nextSample = 0
        autoStopOuter = False
        wasCalledBack = False

        def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
            global nextSample, autoStopOuter, wasCalledBack  ## TODO: FIX?
            wasCalledBack = True
            destEnd = nextSample + noOfSamples
            sourceEnd = startIndex + noOfSamples
            # print(startIndex, sourceEnd)
            bufferCompleteA[nextSample:destEnd] = self._buffers['A'][startIndex:sourceEnd] * conversion_factor
            bufferCompleteB[nextSample:destEnd] = self._buffers['B'][startIndex:sourceEnd] * conversion_factor
            bufferCompleteC[nextSample:destEnd] = self._buffers['C'][startIndex:sourceEnd] * conversion_factor
            bufferCompleteD[nextSample:destEnd] = self._buffers['D'][startIndex:sourceEnd] * conversion_factor
            bufferCompleteE[nextSample:destEnd] = self._buffers['E'][startIndex:sourceEnd] * conversion_factor
            nextSample += noOfSamples
            if autoStop:
                autoStopOuter = True

        # Convert the python function into a C function pointer.
        cFuncPtr = ps.StreamingReadyType(streaming_callback)
        # print("Started streaming")
        start = time.time()
        # Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
        while nextSample < total_samples and not autoStopOuter:
            wasCalledBack = False
            self.status["getStreamingLastestValues"] = ps.ps4000aGetStreamingLatestValues(self.chandle, cFuncPtr, None)
            # print(wasCalledBack)
            if not wasCalledBack:
                # If we weren't called back by the driver, this means no data is ready. Sleep for a short while
                # before trying again.
                time.sleep(0.005)

        # print("Done streaming", time.time() - start)

        return bufferCompleteA, bufferCompleteB, bufferCompleteC, bufferCompleteD, bufferCompleteE

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing Picoscope")
        # Stop the scope
        self.status["stop"] = ps.ps4000aStop(self.chandle)
        pf.assert_pico_ok(self.status["stop"])

        # TODO: For some reason it isnt disconnecting
        # Disconnect the scope
        self.status["close"] = ps.ps4000aCloseUnit(self.chandle)
        pf.assert_pico_ok(self.status["close"])


from multiprocessing import Event, Process, Queue


def run_pico(queue: Queue, stop_flag: Event, *pico_args):
    # Buffer size:
    # 10000  => ~30% extra time
    # 100000 => ~<1% extra time
    with Picoscope(buffer_size=100000, *pico_args) as v:
        for i in range(10):
            data = v.stream(1000000, )  # fs * seconds)
            queue.put(data)
            if stop_flag.is_set():
                break
        else:
            stop_flag.set()
        print("Put data!")


def main():
    from positioning.file_helper import ChunkedWriter

    filename = "picoscope_sample_2.csv"

    seconds = 4  # int or None
    fs = 1e6

    q = Queue()
    stop = Event()

    proc = Process(target=run_pico, args=(q, stop,))
    proc.start()
    with ChunkedWriter(filename, header="A,B,C,D,E") as out:
        while (not stop.is_set()) or (q.qsize() > 0):
            item = q.get()
            print("Row Got")
            out.write(np.vstack(item).T)
            print("Row Written")
    proc.join()


if __name__ == '__main__':
    main()
