from itertools import count
from multiprocessing import Process

import numpy as np

from positioning.VN1000 import VN1000
from positioning.file_helper import ChunkedWriter


def main():
    filename = "./data/unsorted/vn1000_sample.csv"

    seconds = 60 * 60  # int or None
    print(f"Reading for {seconds} seconds.")

    data = np.zeros((1, 6,))

    with VN1000() as v, ChunkedWriter(filename, header="yaw,pitch,roll,a_x,a_y,a_z") as out:
        vn_proc = Process(target=v.stream)
        vn_proc.start()
        for i in (count(start=0) if seconds is None else range(int(seconds * v.fs))):
            d = v.queue.get()
            data[0, :] = d
            out.write(data)
            if i % (v.fs * 60 * 5) == 0:
                print(i)
                print(v.queue.qsize())

        v.stop_flag.set()
        vn_proc.join()


if __name__ == '__main__':
    main()
