#! /usr/bin/python3
from multiprocessing import Process, Event
from multiprocessing.managers import BaseManager

from time import time, sleep, strftime
import os

from positioning.VN1000 import record_vn1000
from positioning.async_picoscope import record_pico
from positioning.counter import Counter
from positioning.omega import record_omega


def main():
    run_name = "test_" + strftime('%y_%m_%d-%H-%M_%S')
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
    # om_proc = Process(target=record_omega,
    #                   kwargs={"filename": (data_dir + "pressure.csv"), "port": "/dev/ttyUSB1", "stop_flag": stop_flag,
    #                           "counter": counter, })
    pico_proc = Process(target=record_pico,
                        kwargs={"filename": (data_dir + "pico.npts"), "stop_flag": stop_flag,
                                "counter": counter, })
    vn_proc.start()
    # om_proc.start()
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
    # om_proc.join()
    vn_proc.join()
    # pico_proc.join()  # TODO: Figure out how to stop pico streaming, or to start unlimited length streaming

    print("Recorded: ", str(counter))


if __name__ == '__main__':
    main()
