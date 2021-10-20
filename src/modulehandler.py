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
        #self._workers["1"] = Module(id=1, ip="129.168.0.1", name="myThread", type="Cisco")
        #self._workers["1"].setDaemon(True)
        #self._workers["1"].start()
            self.get_data_from_devices()
            time.sleep(5)
        #self._workers["1"].stop()

    def import_module(self, filename, packagename):
        if packagename not in self._imported_modules:
            exec(f"from src.modules.{filename} import {packagename}", globals())
            self._imported_modules.append(packagename)
            print(f"Successfully imported module {packagename}")

    def get_data_from_devices(self):
        output = {}
        devices = []
        for deviceid in self._workers:
            devices.append({"id": deviceid,
                            "data": self._workers[deviceid].data})
        if devices != []:
            output["devices"] = devices
            self._api.send_data(output)
            print(output)

    def check_devices(self):
        runningDevices = self.get_running_devices()
        devicesToStart = self._utilities.compare_dict(runningDevices, self._workers)
        devicesToStop = self._utilities.compare_dict(self._workers, runningDevices)

        # starts new Devices
        for cID in devicesToStart:
            type = runningDevices[cID]["type"]
            ip = runningDevices[cID]["ip"]
            name = runningDevices[cID]["name"]
            self.import_module(filename=type.lower(), packagename=type)
            self.start_device(Device(id=cID, name=name, type=type, ip=ip))
            print(runningDevices[cID])

        #stop devices
        for cID in devicesToStop:
            self.stop_device(self._workers[cID].device)


    def start_device(self, device: Device):
        code = f"global cmodule;cmodule = {device.type}(deviceid={device.id},devicetype='{device.type}',devicename='{device.name}',deviceip='{device.ip}')"
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
        for cDevice in running_devices:
            id = cDevice["id"]
            del cDevice["id"]
            output[id] = cDevice
        return output