# A Very rudimentary Serial based driver for the VectorNav VN-1000
import signal
import time
from multiprocessing import Queue, Event, Process
from queue import Empty

import numpy as np
import serial
import time
from positioning.counter import Counter
from positioning.file_helper import ChunkedWriter


class VN1000:
    fs: int = 50

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
        print("Opening VN1000")
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
            self.received.extend(lines[1:])

            while len(self.received) > 1:
                line = self.received.pop(0).strip()
                if len(line) != 93 or line[0:6] != '$VNYIA':
                    continue

                fields = line.split(',')
                # msg_type = fields[0]  # $VNYIA
                angles = fields[1:4]  # yaw, pitch, roll in the local North, East, Down frame
                accel = fields[4:7]  # IN NED frame !!!!!!!
                yaw_rate = fields[7:10]
                yaw_rate[2] = yaw_rate[2][:yaw_rate[2].rfind('*')]
                # checksum = fields[10]

                # TODO anything more efficient than __float__ conversion?
                self.queue.put((time.time(), tuple(map(float, angles + accel + yaw_rate))))
                # TODO: Stop if queue is too big, either integrate the accel values, or drop,

            # while len(self.received) > 1:
            #     line = self.received.pop(0)
            #     if len(line) != 121 or line[0:6] != '$VNYMR':
            #         continue
            #     # if not crc_check(line):
            #     #     continue
            #
            #     fields = line.split(',')
            #
            #     # msg_type = fields[0]  # $VNYMR
            #     angles = fields[1:4]  # yaw, pitch, roll in the local North, East, Down frame
            #     # mag = fields[4:7]
            #     accel = fields[7:10]  # a_x, a_y, and a_z
            #     # alpha = fields[10:13]
            #     # checksum = fields[13]
            #
            #     # TODO anything more efficient than __float__ conversion?
            #     self.queue.put((time.time(), tuple(map(float, angles + accel))))
            #     # TODO: Stop if queue is too big, either integrate the accel values, or drop,

            time.sleep(self.sleep_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing VN1000")
        if self.serial:
            self.serial.close()


def run_vn1000(port, q: Queue, stop_flag: Event):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    with VN1000(port=port, queue=q, stop_flag=stop_flag) as vn:
        vn.stream()


def record_vn1000(filename: str, port: str, stop_flag: Event, counter: Counter = Counter()):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    q = Queue()
    om_proc = Process(target=run_vn1000, args=(port, q, stop_flag))
    om_proc.start()
    print("started vn1000 proc")
    with ChunkedWriter(filename, header="time, yaw, pitch, roll, a_n, a_e, a_d, w_y, w_p, w_r") as out:
        data = np.zeros((1, 10,))
        while q.qsize() > 0 or (not stop_flag.is_set()):
            try:
                d = q.get(block=False)
                data[0, 0] = d[0]  # Timestamp
                data[0, 1:] = d[1]
                out.write(data)
                counter.inc_imu()
            except Empty:
                if stop_flag.is_set():
                    break
                time.sleep(0.05)

        om_proc.join()


if __name__ == '__main__':
    pass
