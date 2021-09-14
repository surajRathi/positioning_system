picoscope.py, dummy_picoscope.py := 
    Export class `Picoscope` which is a context manager providing the `stream` function to receive data as a tuple of numpy arrays.
    Reads a very large batch of readings at a time

async_picoscope.py :=
    UProvides picoscope readings in real-time in chunks.

vn1000.py, dummy_vn1000.py :=
    Export class `VN1000` which is a context manager. When the `stream` function is called, the `VN1000.queue` will be fed. `VN1000.stop_flag.set()` can be used to stop the vn1000.
    It currently provides readings in batches of 1.

zero_crossing.py :=
    Exports `Est_ZC_stage_1` this takes the signal, win_size, fs, and std_noise_multiplier. Returns the index of start of sound wave.
    On error: returns zero (I think)
    TODO: Requires cleanup
          itertools operations might be replaceable with numpy vectorization


triangulate.py :=
    Exports `gps_solve`. Requires distances and pinger location

