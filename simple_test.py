import numpy as np

from positioning.dummy_picoscope import Picoscope
from positioning.triangulate import gps_solve
from positioning.zero_crossing import Est_ZC_stage_1


def main():
    data = None
    with Picoscope() as p:
        data = p.stream()
    print(data.shape)
    v_sound = 1500
    fs = 1e6
    window_size = 500
    multiplier = 10  # std_noise_multiplier

    indices = [
        Est_ZC_stage_1(channel, window_size, fs, multiplier)
        for channel in data.T
    ]
    print(indices)
    # indices = Est_ZC_stage_1(data, window_size, fs, multiplier)

    zero_index = indices[0]
    dists = np.array([(index - zero_index) * v_sound / fs for index in indices[1:]])

    hydrophone_locs = np.array([
        [1.70, 0.0, 0.75],
        [0.80, 8.85, 0.25],
        [0.0, 4.25, 0.55],
        [3.0, 4.50, 1.20]
    ])

    coords = gps_solve(dists, hydrophone_locs)

    print(coords)


if __name__ == '__main__':
    main()
