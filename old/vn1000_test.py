from multiprocessing import Process, Queue, Event
from sys import argv

import numpy as np


def get_line_count(filename: str):
    import subprocess
    return int(subprocess.run(["wc", "-l", filename], capture_output=True).stdout.decode('UTF-8').split(' ')[0])


def run_vn1000(queue: Queue, stop_flag: Event, filename=None):
    if filename is None:
        from positioning.VN1000 import VN1000
        device = VN1000(port='/dev/ttyUSB0', queue=queue, stop_flag=stop_flag)
    else:
        from positioning.dummy_vn1000 import VN1000
        device = VN1000(filename, queue=queue, stop_flag=stop_flag)

    with device as v:
        v.stream()

    print("Done")


def main():
    filename = None
    if len(argv) == 2:
        filename = argv[1]

    fs = 40  # TODO: Check
    dt = 1.0 / fs
    accel_correction = -np.array([0.1752296, 0.1025151, -9.581222])

    num_samples = int(1e4) if filename is None else get_line_count(filename)
    accel = np.zeros((num_samples, 3,))
    orien = np.zeros((num_samples, 3,))
    accel.fill(np.nan)
    orien.fill(np.nan)

    q = Queue()
    stop = Event()
    vn_proc = Process(target=run_vn1000, args=(q, stop, filename))
    vn_proc.start()
    try:
        for i in range(num_samples):
            t, d = q.get()
            d = np.array(d)
            if len(d) == 0:
                break
            orien[i, :] = d[0:3]
            accel[i, :] = d[3:6]
    except KeyboardInterrupt:
        pass

        stop.set()
        print("Stopping")
        vn_proc.join()

    print("plotting", accel.shape)
    print(np.nanmean(accel, axis=0))
    accel += accel_correction
    print(np.nanmean(accel, axis=0))

    v = np.cumsum(accel, axis=0) * dt
    x = np.cumsum(v, axis=0) * dt

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 2)

    ax[0, 0].plot(accel[:, 0], color='r')
    ax[0, 0].plot(accel[:, 1], color='g')
    ax[0, 0].plot(accel[:, 2], color='b')
    ax[0, 0].set_title("Accel")

    ax[0, 1].plot(orien[:, 0], color='r')
    ax[0, 1].plot(orien[:, 1], color='g')
    ax[0, 1].plot(orien[:, 2], color='b')
    ax[0, 1].set_title("orien")

    ax[1, 0].set_aspect('equal', adjustable='datalim')
    ax[1, 0].plot(x[:, 0] * 100, x[:, 1] * 100)
    ax[1, 0].set_title("XY Path (cm)")

    ax[1, 1].plot(x[:, 0], color='r')
    ax[1, 1].plot(x[:, 1], color='g')
    ax[1, 1].plot(x[:, 2], color='b')
    ax[1, 1].set_title("displacement")

    ax[2, 0].plot(v[:, 0], color='r')
    ax[2, 0].plot(v[:, 1], color='g')
    ax[2, 0].plot(v[:, 2], color='b')
    ax[2, 0].set_title("Velocity")

    plt.show()

    np.savetxt('imu_test_1.csv', accel)


if __name__ == '__main__':
    main()
