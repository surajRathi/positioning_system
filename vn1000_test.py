from multiprocessing import Process

import numpy as np

from positioning.VN1000 import VN1000


def main():
    fs = 40  # TODO: Check
    dt = 1.0 / fs

    num_samples = int(1e3)
    accel = np.zeros((num_samples, 3,))
    orien = np.zeros((num_samples, 3,))

    with VN1000() as v:
        vn_proc = Process(target=v.stream)
        vn_proc.start()
        for i in range(num_samples):
            d = v.queue.get()
            accel[i, :] = d[0:3]
            orien[i, :] = d[3:6]

        v.stop_flag.set()
        vn_proc.join()

    # v = np.trapz(accel, dx=dt)
    # x = np.trapz(v, dx=dt)

    v = np.cumsum(accel, axis=1) * dt
    x = np.cumsum(v, axis=1) * dt

    import matplotlib.pyplot as plt
    # plt.plot(x[:,0], x[:,1])
    # plt.plot(x[:,0])
    # plt.plot(x[:,1])
    # plt.plot(x[:,2])
    plt.plot(accel[:, 0], color='r')
    plt.plot(accel[:, 1], color='g')
    plt.plot(accel[:, 2], color='b')
    plt.show()
    plt.close()
    plt.plot(x[:, 0], x[:, 1])
    plt.show()
    plt.close()
    plt.plot(x[:, 0])
    plt.plot(x[:, 1])
    plt.plot(x[:, 2])
    plt.show()
    plt.close()
    np.savetxt('imu_test_1.csv', accel)


if __name__ == '__main__':
    main()
