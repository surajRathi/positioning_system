# A Very rudimentry Serial based driver for the VectorNav VN-1000

import time
from multiprocessing import Queue, Event

import serial


class VN1000:
    def __init__(self, port='/dev/ttyUSB0', baud=115200, sleep_time=0.001, queue=Queue(), stop_flag=Event()):
        self.port = port  # Note: Make sure use has permissions to access the serial port
        self.baud = baud
        self.sleep_time = sleep_time
        self.enabled = False
        self.serial = None
        self.queue = queue
        self.stop_flag = stop_flag
        self.strs = ['']

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
            self.strs[0] += lines[0]
            self.strs.extend(lines[1:])

            while len(self.strs) > 1:
                line = self.strs.pop(0)
                if len(line) != 121 or line[0:6] != '$VNYMR':
                    continue
                # if not crc_check(line):
                #     continue

                fields = line.split(',')

                angles = fields[1:4]  # yaw, pitch, roll in the local North, East, Down frame 
                mag = fields[4:7]
                accel = fields[7:10]
                alpha = fields[10:13]

                # TODO dont use float in map
                self.queue.put(tuple(map(float, angles + accel)))
                # TODO: Stop if queue is too big, either integrate the accel values, or drop,

                # print(f"{time.time_ns() % 100000:05}\t{angles}\t{accel}")

            time.sleep(self.sleep_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing VN1000")
        if self.serial:
            self.serial.close()


if __name__ == '__main__':
    from multiprocessing import Process, Event, Queue

    # q = Queue()
    # stop = Event()
    # with VN1000(queue=q, stop_flag=stop) as v:
    #     vn_proc = Process(target=v.stream)
    #     vn_proc.start()
    #     for i in range(int(1e2)):
    #         print(q.get())
    #     stop.set()
    #     vn_proc.join()

    n_samples = int(1e3)
    with VN1000() as v:
        vn_proc = Process(target=v.stream)
        vn_proc.start()
        for i in range(n_samples):
            print(*(str(x).zfill(6) for x in v.queue.get()))  # v.queue.qsize(),
        v.stop_flag.set()
        vn_proc.join()
