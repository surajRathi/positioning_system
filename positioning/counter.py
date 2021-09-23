import dataclasses
import time


@dataclasses.dataclass
class Counter:
    t_start: float = 0
    pico: int = 0
    imu: int = 0
    pres: int = 0

    def set_t(self, time: float):
        self.t_start = time

    def inc_pico(self):
        self.pico += 1

    def inc_imu(self):
        self.imu += 1

    def inc_pres(self):
        self.pres += 1

    def __str__(self):
        return f"{time.time() - self.t_start:.2f}\tPico: {self.pico}\tIMU: {self.imu}\tPres: {self.pres}\t"
