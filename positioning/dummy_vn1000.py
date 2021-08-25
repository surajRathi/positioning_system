import queue
import time
from multiprocessing import Queue, Event

if __name__ == '__main__':
    from file_helper import FileLoader
else:
    from positioning.file_helper import FileLoader


class VN1000:
    g: float = 9.572136
    def __init__(self, filename='./data/vn1000/square_motion_with_turn.csv', sleep_time=0, queue=Queue(),
                 stop_flag=Event()):
        self.filename = filename
        self.loader = None
        self.sleep_time = sleep_time
        self.queue = queue
        self.stop_flag = stop_flag

    def __enter__(self):
        print(f"Opening {self.filename}")
        self.loader = iter(FileLoader(self.filename, skip_rows=1, chunk_size=1))
        return self

    def stream(self):
        try:
            while not self.stop_flag.is_set():
                self.queue.put(tuple(next(self.loader)))
                time.sleep(self.sleep_time)
        except StopIteration:
            pass
        self.stop_flag.set()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing VN1000")
        # self.loader.__exit__(exc_type, exc_val, exc_tb)


if __name__ == '__main__':
    from multiprocessing import Process

    with VN1000() as v:
        vn_proc = Process(target=v.stream)
        vn_proc.start()
        while not v.stop_flag.is_set():
            try:
                print(*(str(x).zfill(6) for x in v.queue.get(block=False)))  # v.queue.qsize(),
            except queue.Empty:
                pass
        
        vn_proc.join()
