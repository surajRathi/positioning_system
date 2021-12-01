#! /usr/bin/python3
from multiprocessing import Process, Event
from multiprocessing.managers import BaseManager

from time import time, sleep, strftime
import os

from positioning.VN1000 import record_vn1000
from positioning.counter import Counter


def main():
    run_name = "air_enclosure_long_test_" + strftime('%d%m%y-%H-%M_%S')
    data_dir = f"./data/imu_tests/{run_name}/"
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
    vn_proc.start()

    print("Started: press Control+C to stop")
    try:
        for i in range(100):
            sleep(2)
            print(str(counter))
    except KeyboardInterrupt:
        print("Keyboard Interrupt, stopping.")

    stop_flag.set()
    vn_proc.join()
    print("Recorded: ", str(counter))


if __name__ == '__main__':
    main()
