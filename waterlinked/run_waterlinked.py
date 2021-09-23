"""
Push depth to Water Linked Underwater GPS
"""
import csv
import json
import logging
import os
import time
from datetime import datetime
from multiprocessing import Event, Process, Manager

import requests
import websockets

from omega import run_omega

log = logging.getLogger()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class ROV:
    def __init__(self):
        self.depth = 0
        self.thickness = 0
        self.url = ""
        self.temp = 0
        self.Time = ""

    def get_position(self):
        return self.Time

    def get_data(self, url):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as exc:
            print("Exception occured {}".format(exc))
            return None

        if r.status_code != requests.codes.ok:
            print("Got error {}: {}".format(r.status_code, r.text))
            return None

        return r.json()

    def get_acoustic_position(self, base_url, writer, depth, thickness):
        data = self.get_data("{}/api/v1/position/acoustic/filtered".format(base_url))
        print(data)
        if data:
            t = self.get_time()
            t += [data['x'], data['y'], depth, thickness]
            self.Time = t
            writer.writerow(t)
        return data

    def get_global_position(self, base_url):
        return self.get_data("{}/api/v1/position/global".format(base_url))

    def get_time(self):
        dt = datetime.now()
        return [str(dt.year) + str('-') + str(dt.month) + str('-') + str(dt.day),
                str(dt.hour) + str(':') + str(dt.minute) + str(':') + str(dt.second) + str(':') + str(
                    dt.microsecond // 1000)]

    def insert(self, x, y, z, filename):
        t = self.get_time()
        with open(filename, mode='a') as file:
            writer = csv.writer(file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            t += [x, y, z]
            self.Time = t
            writer.writerow(t)

    async def hello(self, url):
        uri = "ws://" + url + ":8089/echo/"
        print("uri ", uri)
        async with websockets.connect(uri) as websocket:
            # name = input("What's your name, faaty? ")

            await websocket.send("Hello")
            # print(f"> {}")
            recv_data = await websocket.recv()
            data = json.loads(recv_data)
            self.depth = float(data['depth'])
            self.thickness = float(data['thickness'])
            # print(f"< {greeting}")

    def get_depth(self):
        return self.depth

    def set_depth(self, url, depth, temp):
        payload = dict(depth=self.depth, temp=self.temp)
        r = requests.put(url, json=payload, timeout=10)
        if r.status_code != 200:
            log.error("Error setting depth: {} {}".format(r.status_code, r.text))


def main():
    rov = ROV()

    rov.url = "http://192.168.1.107"
    rov.depth = 1
    rov.temp = 30
    repeat_time = 1
    t_now = (datetime.now())
    t_now = str(t_now.strftime("%H")) + '-' + str(t_now.strftime("%M")) + '-' + str(t_now.strftime("%S"))

    # ROV URlL
    # asyncio.get_event_loop().run_until_complete(hello("192.168.1.127"))

    log.info("Using baseurl: %s depth: %f temperature %f",
             rov.url, rov.depth, rov.temp)

    m = Manager()
    depth = m.Value('c_double', 0)

    stop_flag = Event()

    om_proc = Process(target=run_omega, args=('COM7', depth, stop_flag))
    om_proc.start()

    print("Starting Waterlinked")

    try:
        os.mkdir('./data')
    except:
        pass
    try:
        os.mkdir('./data/waterlinked')
    except:
        pass

    with open(f"./data/waterlinked/_{t_now}.csv", mode='a') as file:
        writer = csv.writer(file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        while True:
            log.info('Sending depth')
            d = depth.value
            rov.set_depth('{}/api/v1/external/depth'.format(rov.url), d, rov.temp)
            print("depth", d)
            data = rov.get_acoustic_position(rov.url, writer, rov.depth, rov.thickness)
            # print ("depth",depth)
            if repeat_time <= 0:
                break

            log.info('Waiting %d seconds', repeat_time)
            time.sleep(repeat_time)


if __name__ == "__main__":
    main()
