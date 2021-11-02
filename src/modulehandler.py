import threading
import json
from src.io import API, Config
from src.modules.module import Module
from src.device import Device
from src.utilities import Utilities
import time


class ModuleHander():
    def __init__(self):
        self._imported_modules = []
        self._workers = {}
        self._running = True
        self._api = API()
        self._utilities = Utilities()
        self.mainloop()

    def mainloop(self):
        while self._running:
            self.check_devices()
            self.get_data_from_devices()
            time.sleep(5)

    def import_module(self, filename, packagename):
        if packagename not in self._imported_modules:
            exec(f"from src.modules.{filename} import {packagename}", globals())
            self._imported_modules.append(packagename)
            print(f"Successfully imported module {packagename}")

    def get_data_from_devices(self):
        output = {}
        devices = []
        for deviceid in self._workers:
            c_data = self._workers[deviceid].data
            if c_data:
                devices.append({"id": deviceid,
                                "type": self._workers[deviceid].device.type,
                                "data": c_data})
        if devices != []:
            output["devices"] = devices
            self._api.send_data(output)
            print(output)

    def check_devices(self):
        running_devices = self.get_running_devices()
        devices_to_start = self._utilities.compare_dict(running_devices, self._workers)
        devices_to_stop = self._utilities.compare_dict(self._workers, running_devices)

        # starts new Devices
        for c_id in devices_to_start:
            device_type = running_devices[c_id]["type"]
            ip = running_devices[c_id]["ip"]
            name = running_devices[c_id]["name"]
            timeout = running_devices[c_id]["timeout"]
            self.import_module(filename=device_type.lower(), packagename=device_type)
            self.start_device(Device(id=c_id, name=name, type=device_type, ip=ip, timeout=timeout))
            print(running_devices[c_id])

        # stop devices
        for c_id in devices_to_stop:
            self.stop_device(self._workers[c_id].device)

        # update timeout and check for dead devices/threads and restart them
        for c_id in running_devices:
            # check if device is still running. if not, restart it.
            if not self._workers[c_id].is_alive() or self._workers[c_id].is_stopped():
                c_device = self._workers[c_id].device
                self.start_device(c_device)
            # update timeout
            self._workers[c_id].device.timeout = running_devices[c_id]["timeout"]

    def start_device(self, device: Device):
        code = f"global cmodule;cmodule = {device.type}(deviceid={device.id},devicetype='{device.type}',devicename='{device.name}',deviceip='{device.ip}', devicetimeout={device.timeout})"
        exec(code, globals())
        self._workers[device.id] = cmodule
        self._workers[device.id].setDaemon(True)
        self._workers[device.id].start()
        print(f"Started device {device.name}")
        return True

    def stop_device(self, device: Device):
        self._workers[str(device.id)].stop()
        del self._workers[str(device.id)]
        print(f"Stopped device {device.name}")
        return True

    def get_running_devices(self):
        running_devices = self._api.get_running_threads()
        output = {}
        for c_device in running_devices:
            device_id = c_device["id"]
            del c_device["id"]
            output[device_id] = c_device
        return output