from itertools import count
from multiprocessing import Process, Queue, Event

from positioning.file_helper import ChunkedWriter
from positioning.omega import Omega


def run_omega(queue: Queue, stop_flag: Event):
    device = Omega(port='COM7', queue=queue, stop_flag=stop_flag)

    with device as v:
        v.stream()

    print("Done")


def main():
    filename = "./data/unsorted/wintest_omega_sample.csv"

    seconds = 60  # int or None
    print(f"Reading for {seconds} seconds.")

    q = Queue()
    stop = Event()
    om_proc = Process(target=run_omega, args=(q, stop))
    om_proc.start()
    with ChunkedWriter(filename, header="mV") as out:
        for i in (count(start=0) if seconds is None else range(int(seconds * 20))):
            d = q.get()
            out.write((d,))
            if i % (20 * 60 * 5) == 0:
                print(i)
                print(q.qsize())

        stop.set()
    om_proc.join()


if __name__ == '__main__':
    main()
