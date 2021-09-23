# A Very rudimentary Serial based driver for the VectorNav VN-1000
import signal
import time
from multiprocessing import Event, Process
from multiprocessing import Manager

import serial


class Omega:
    fs: int = 20

    def __init__(self, port='/dev/ttyUSB0', baud=9600, sleep_time=0.001, depth=None, stop_flag=Event()):
        self.port = port  # Note: Make sure use has permissions to access the serial port
        self.baud = baud
        self.sleep_time = sleep_time
        self.enabled = False
        self.serial = None
        self.depth = depth
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
                    print(int(line) * 0.382394)
                    depth.value = int(line) * 0.382394
                except ValueError:
                    pass
            time.sleep(self.sleep_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing Omega")
        if self.serial:
            self.serial.close()


def run_omega(port, depth, stop_flag: Event):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    with Omega(port=port, depth=depth, stop_flag=stop_flag) as om:
        om.stream()


if __name__ == '__main__':
    m = Manager()
    depth = m.Value('c_double', 0)

    stop_flag = Event()
    om_proc = Process(target=run_omega, args=('COM7', depth, stop_flag))

    try:
        while True:
            # print(depth.value)
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_flag.set()
    om_proc.join()
