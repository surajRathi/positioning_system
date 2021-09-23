from itertools import count
from multiprocessing import Process, Queue, Event

import numpy as np

from positioning.VN1000 import VN1000
from positioning.file_helper import ChunkedWriter


def run_vn1000(queue: Queue, stop_flag: Event):
    from positioning.VN1000 import VN1000
    device = VN1000(port='COM6', queue=queue, stop_flag=stop_flag)

    with device as v:
        v.stream()

    print("Done")


def main():
    filename = "./data/unsorted/wintest_vn1000_sample.csv"

    seconds = 10  # int or None
    print(f"Reading for {seconds} seconds.")

    data = np.zeros((1, 6,))

    q = Queue()
    stop = Event()
    vn_proc = Process(target=run_vn1000, args=(q, stop))
    vn_proc.start()
    with ChunkedWriter(filename, header="yaw,pitch,roll,a_x,a_y,a_z") as out:
        for i in (count(start=0) if seconds is None else range(int(seconds * 80))):
            d = q.get()
            data[0, :] = d
            out.write(data)
            if i % (40 * 60 * 5) == 0:
                print(i)
                print(q.qsize())

        stop.set()
        vn_proc.join()


if __name__ == '__main__':
    main()
