import numpy as np
from scipy.optimize import minimize


def gps_solve(distances_from_stations: np.array, stations_coordinates: np.array):
    # TODO Check for close form solution
    def error(x, c, r):
        return np.sum((np.linalg.norm(x - c, axis=1) - r) ** 2)
        # return sum([(np.linalg.norm(x - c[i]) - r[i]) ** 2 for i in range(len(c))])

    l = len(stations_coordinates)
    S = sum(distances_from_stations)

    # Initial guess is weighted average (by distance) of station coordinates

    # W = [((l - 1) * S) / (S - w) for w in distances_to_station]
    # x0 = sum([W[i] * stations_coordinates[i] for i in range(l)])
    x0 = np.dot(distances_from_stations, stations_coordinates) / np.sum(distances_from_stations)

    # optimize distance from signal origin to border of spheres
    return minimize(error, x0, args=(stations_coordinates, distances_from_stations), method='Nelder-Mead').x


# Pinger co-ordinates = [1 ,1, 1]
# Location of hdphones = [1.70,0.0, 0.75] , [0.80, 8.85, 0.25], [0.0, 4.25, 0.55], [3.0, 4.50, 1.20]
# Radius of spheres = [1.2459, 7.8882, 3.4300, 4.0360] #respectively

if __name__ == "__main__":
    landmarks = np.array([
        [1.70, 0.0, 0.75],
        [0.80, 8.85, 0.25],
        [0.0, 4.25, 0.55],
        [3.0, 4.50, 1.20]
    ])

    distances_to_station = np.array([1.2459, 7.8882, 3.4300, 4.0360])

    coords = gps_solve(distances_to_station, landmarks)
    print('\033[95m' + 'Co-ordinates of the pinger = ' + str(coords) + '\033[95m\033[0m')
