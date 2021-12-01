import numpy as np

import serial

import matplotlib.pyplot as plt


def parse_line(line):
    try:
        line = bytes([b for b in line if b != 0]).decode('ascii').strip()
        # line = line.decode('ascii').strip()
    except UnicodeDecodeError:  # Malformed byte
        return None
    except OSError:  # Disconnected
        return None

    if len(line) != 93 or line[0:6] != '$VNYIA':
        return None

    fields = line.split(',')
    angles = fields[1:4]  # yaw, pitch, roll in the local North, East, Down frame
    accel = fields[4:7]  # IN NED frame !!!!!!!

    try:
        return tuple(map(float, accel))
    except ValueError:
        return None


def main():
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0)  # Non Blocking
    print('Opened serial')

    f, axes = plt.subplots(3, 1, figsize=(12, 6))
    f.suptitle('Acceleration in NED')
    f.set_tight_layout(True)

    fs = 50
    winsize = 5
    acc_max = 10

    acc = np.zeros((fs * winsize, 3))
    # t = - np.arange(acc.shape[0])[::-1] / fs
    t = np.arange(acc.shape[0]) / fs

    for ax in axes:
        ax.set_xlim(t[0], t[-1])
        ax.set_ylim(-acc_max, acc_max)
        ax.grid()
    f.show()
    f.canvas.draw()
    backgrounds = [f.canvas.copy_from_bbox(ax.bbox) for ax in axes]

    lines = [ax.plot(t, channel)[0] for (ax, channel) in zip(axes, acc.T)]
    print('Starting loop')
    while True:
        # t += 1.0 / fs
        try:
            while True:
                l = ser.readline()
                if len(l) == 0:
                    break
                vals = parse_line(l)
                if vals is None:
                    continue

                acc = np.roll(acc, -1, axis=0)
                acc[-1, :] = vals[:]
        except ValueError:
            pass

        for l, ax, data, bk in zip(lines, axes, acc.T, backgrounds):
            f.canvas.restore_region(bk)
            # l.set_xdata(t)
            l.set_ydata(data)
            ax.draw_artist(l)
            f.canvas.blit(ax.bbox)

        plt.pause(0.1)


if __name__ == '__main__':
    main()
