#! /usr/bin/python3
import threading
from multiprocessing import Process, Event
from multiprocessing.managers import BaseManager

from time import time, sleep, strftime
import os

from positioning.VN1000 import record_vn1000
from positioning.async_picoscope import record_pico
from positioning.counter import Counter


def main():
    run_name = "rov_pretest_" + strftime('%d%m%y-%H-%M_%S')
    data_dir = f"./data/full/{run_name}/"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    BaseManager.register('Counter', Counter)
    m = BaseManager()
    m.start()
    counter = m.Counter()

    counter.set_t(time())

    stop_flag = Event()

    vn_proc = Process(target=record_vn1000,
                      kwargs={"filename": (data_dir + "imu.csv"), "port": "/dev/ttyUSB0", "stop_flag": stop_flag,
                              "counter": counter, })

    def read_kbd_input(filename, stop_flag):
        print('Ready for keyboard input:')
        with open(filename, 'a') as f:
            while True:
                input_str = input()
                print(time(), input_str, file=f)
                print("Note:", time())
                f.flush()

    pico_proc = Process(target=record_pico,
                        kwargs={"filename": (data_dir + "pico.npts"), "stop_flag": stop_flag,
                                "counter": counter, })
    vn_proc.start()
    inputThread = threading.Thread(target=read_kbd_input, args=((data_dir + "times.log"), None,), daemon=True)
    inputThread.start()
    pico_proc.start()

    print("Started: press Control+C to stop")
    try:
        for i in range(100):
            sleep(5)
            print(str(counter))
    except KeyboardInterrupt:
        print("Keyboard Interrupt, stopping.")
        pass

    stop_flag.set()
    vn_proc.join()
    # pico_proc.join()  # TODO: Figure out how to stop pico streaming, or to start unlimited length streaming

    print("Recorded: ", str(counter))


if __name__ == '__main__':
    main()
