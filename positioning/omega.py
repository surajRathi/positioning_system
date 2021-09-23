# A Very rudimentary Serial based driver for the VectorNav VN-1000
import signal
import time
from multiprocessing import Queue, Event, Process
from queue import Empty
from time import time as now
import serial

from positioning.counter import Counter
from positioning.file_helper import ChunkedWriter


class Omega:
    fs: int = 20

    def __init__(self, port='/dev/ttyUSB0', baud=9600, sleep_time=0.001, queue=Queue(), stop_flag=Event()):
        self.port = port  # Note: Make sure use has permissions to access the serial port
        self.baud = baud
        self.sleep_time = sleep_time
        self.enabled = False
        self.serial = None
        self.queue = queue
        self.stop_flag = stop_flag
        self.received = ['']

    def __enter__(self):
        print("Opening Omega")
        self.enabled = True
        self.serial = serial.Serial(self.port, self.baud, timeout=0)  # Non Blocking
        return self

    def stream(self):
        while self.serial and not self.stop_flag.is_set():
            try:
                data = self.serial.read(self.serial.inWaiting())
                lines = data.decode('ASCII').split('\r')
            except UnicodeDecodeError:  # Malformed byte
                continue
            except OSError:  # Disconnected 
                break

            self.received[0] += lines[0]
            if len(lines) > 1:
                self.received.extend(lines[1:])

            while len(self.received) > 1:
                line = self.received.pop(0)

                try:
                    self.queue.put((now(), int(line)))
                    # TODO: Stop if queue is too big, either integrate the accel values, or drop,
                except ValueError:
                    pass
            time.sleep(self.sleep_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing Omega")
        if self.serial:
            self.serial.close()


def run_omega(port, q: Queue, stop_flag: Event):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    with Omega(port=port, queue=q, stop_flag=stop_flag) as om:
        om.stream()


def record_omega(filename: str, port: str, stop_flag: Event, counter: Counter = Counter()):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    q = Queue()
    om_proc = Process(target=run_omega, args=(port, q, stop_flag))
    om_proc.start()
    print("started proc")
    with ChunkedWriter(filename, header="time, voltage") as out:
        while q.qsize() > 0 or (not stop_flag.is_set()):
            # print("loop")
            try:
                d = q.get(block=False)
                out.write((d,))
                counter.inc_pres()
            except Empty:
                if stop_flag.is_set():
                    break
                time.sleep(0.05)

        om_proc.join()


if __name__ == '__main__':
    pass
