# A Very rudimentry Serial based driver for the VectorNav VN-1000

from __future__ import with_statement
import numpy as np
import serial
import time

class VN100:
    def __init__(self, port='/dev/ttyUSB0', baud=115200, sleep_time=0.001):
        self.port = port  # Note: Make sure use has permissions to access the serial port
        self.baud = baud
        self.sleep_time = sleep_time  
        self.enabled = False
        self.serial = None
        self.strs = ['']

    def __enter__(self):
        print("Opening VN1000")
        self.enabled = True
        self.serial = serial.Serial(self.port, self.baud, timeout=0) # Non Blocking
        return self

    def stream(self):
        while self.serial:
            data = self.serial.read(self.serial.inWaiting())
            lines = data.decode('ASCII').split('\n')
            self.strs[0] += lines[0]
            self.strs.extend(lines[1:])
            
            while len(self.strs) > 1:
                line = self.strs.pop(0)
                if len(line) != 121:
                    continue
                if line[0] != '$':
                    continue
                # if not crc_check(line):
                #     continue

                fields = line.split(',')
                
                # if fields[0] != "$VNYMR":
                #     continue

                angles = fields[1:4]  # yaw, pitch, roll
                mag = fields[4:7]
                accel = fields[7:10]
                alpha = fields[10:13]

                print(f"{time.time_ns() % 100000:05}\t{angles}\t{accel}")

            time.sleep(self.sleep_time)


    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing VN1000")
        if self.serial:
            self.serial.close()

if __name__ == '__main__':
    with VN100() as v:
        v.stream()