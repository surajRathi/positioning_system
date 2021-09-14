picoscope.py, dummy_picoscope.py := 
    Export class `Picoscope` which is a context manager providing the `stream` function to receive data as a tuple of numpy arrays.
    It currently provides readings in very large batches
    TODO: Refactor

async_picoscope.py :=
    Untested multiprocessing based variant of picoscope.py

vn1000.py, dummy_vn1000.py :=
    Export class `VN1000` which is a context manager. The `stream` function can be run in another process, and the `VN1000.queue` will be fed. `VN1000.stop_flag.set()` can be used to stop it.
    It currently provides readings one at a time.

zero_crossing.py :=
    Exports `Est_ZC_stage_1` this takes the signal, win_size, fs, and std_noise_multiplier. Returns the index of start of sound wave.
    On error: returns zero (I think)
    TODO: Requires cleanup
          itertools operations might be replaceable with numpy vectorization


triangulate.py :=
    Exports `gps_solve`. Requires distances and pinger location

