# A Very rudimentary Serial based driver for the VectorNav VN-1000

import time
from multiprocessing import Queue, Event

import serial


class Omega:
    fs: int = 20

    def __init__(self, port='/dev/ttyUSB0', baud=115200, sleep_time=0.001, queue=Queue(), stop_flag=Event()):
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
                lines = data.decode('ASCII').split('\n')
            except UnicodeDecodeError:  # Malformed byte 
                continue
            except OSError:  # Disconnected 
                break
            self.received[0] += lines[0]
            if len(self.received) > 1:
                self.received.extend(lines[1:])

            while len(self.received) > 1:
                line = self.received.pop(0)

                try:
                    self.queue.put(int(line))
                    # TODO: Stop if queue is too big, either integrate the accel values, or drop,
                except 
            time.sleep(self.sleep_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing Omega")
        if self.serial:
            self.serial.close()


if __name__ == '__main__':
    from multiprocessing import Process, Queue

    n_samples = int(1e2)  # 5 Seconds
    with Omega() as v:
        vn_proc = Process(target=v.stream)
        vn_proc.start()
        for i in range(n_samples):
            print(*(str(x).zfill(6) for x in v.queue.get()))  # v.queue.qsize(),
        v.stop_flag.set()
        vn_proc.join()
