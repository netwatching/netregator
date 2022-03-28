import threading
import json
from src.io import API, Config
from src.device import Device
from src.utilities import Utilities
import time
import os
from decouple import config
from src.utilities import Utilities
import importlib


class DeviceHandler:
    def __init__(self):
        self._logger = Utilities.setup_logger()
        self._imported_modules = []
        self._workers = {}
        self._module_config = Config("./src/config/modules.json").get_whole_file()
        self._system_threads = {}
        self._known_system_threads = ["sendData", "checkDevices"]
        self._running = True
        self._api = API()
        self._utilities = Utilities()
        self._modules = Config("./src/config/modules.json")
        self.mainloop()

    def mainloop(self):
        try:
            self.start_system_thread()
            time.sleep(1)
            self.set_version()
            self.set_modules()
            while self._running:
                self.check_system_threads()
                time.sleep(5)
        except KeyboardInterrupt:
            os._exit(1)

    def get_data_from_devices(self):
        while True:
            output = {}
            devices = []
            external_events = {}
            for device_id in self._workers:
                c_data, c_external_events = self._workers[device_id].data
                self._workers[device_id].clear_data()
                if c_data != {'static_data': [], 'live_data': [], 'events': {}}:
                    current_metadata = {"id": device_id,
                                        "name": self._workers[device_id].name,
                                        "ip": self._workers[device_id].ip}
                    current_metadata.update(c_data)
                    devices.append(current_metadata)
                self._workers[device_id].clear_data()
                for c_hostname in c_external_events:
                    if not c_hostname in external_events:
                        external_events[c_hostname] = []
                    external_events[c_hostname] = external_events[c_hostname] + c_external_events[c_hostname]

            if devices != [] or external_events != {}:
                output["devices"] = devices
                output["external_events"] = external_events
                self._api.send_data(output)
                # print("--------------\n"*4)
                self._logger.debug(json.dumps(output))
            time.sleep(5)

    def check_devices(self):
        while True:
            running_devices = self.get_running_devices()
            print(running_devices)
            devices_to_start = Utilities.compare_dict(running_devices, self._workers)
            devices_to_stop = Utilities.compare_dict(self._workers, running_devices)

            # starts new Devices
            for c_id in devices_to_start:
                device_type = running_devices[c_id]["type"]
                ip = running_devices[c_id]["ip"]
                name = running_devices[c_id]["hostname"]
                timeout = running_devices[c_id]["timeout"]
                modules = running_devices[c_id]["modules"]
                self.start_device(
                    Device(id_=c_id, name=name, device_type=device_type, ip=ip, timeout=timeout, modules=modules))
                # print(running_devices[c_id])

            # stop devices
            for c_id in devices_to_stop:
                self.stop_device(self._workers[c_id].id, self._workers[c_id].name)

            # update timeout, modules and check for dead devices/threads and restart them
            for c_id in running_devices:
                # check if device is still running. if not, restart it.
                if not self._workers[c_id].is_alive() or not self._workers[c_id].running:
                    c_id = self._workers[c_id].id
                    name = self._workers[c_id].name
                    device_type = self._workers[c_id].device_type
                    ip = self._workers[c_id].ip
                    timeout = self._workers[c_id].timeout
                    modules = self._workers[c_id].modules
                    self.start_device(
                        Device(id_=c_id, name=name, device_type=device_type, ip=ip, timeout=timeout, modules=modules))
                # update timeout
                self._workers[c_id].timeout = running_devices[c_id]["timeout"]
                self._workers[c_id].modules = running_devices[c_id]["modules"]
            time.sleep(5)

    def start_device(self, device: Device):
        c_device = Device(id_=device.id, name=device.name, ip=device.ip, device_type=device.device_type,
                          timeout=device.timeout, modules=device.modules)
        self._workers[device.id] = c_device
        self._workers[device.id].start()
        self._logger.info(f"Started device {device.name}")
        return True

    def start_system_thread(self, key=None):
        if key == "sendData" or key is None:
            self._system_threads["sendData"] = threading.Thread(target=self.get_data_from_devices, name="sendData",
                                                                args=())
            self._system_threads["sendData"].start()
        if key == "checkDevices" or key is None:
            self._system_threads["checkDevices"] = threading.Thread(target=self.check_devices, name="checkDevices",
                                                                    args=())
            self._system_threads["checkDevices"].start()

    def stop_system_thread(self, key=None):
        if key is None:
            for c_key in self._known_system_threads:
                self._system_threads[c_key].terminate()

    def check_system_threads(self):
        for c_key in self._known_system_threads:
            if not self._system_threads[c_key].is_alive():
                self.start_system_thread(c_key)
        for c_key in self._utilities.compare_list(self._known_system_threads, self._system_threads):
            self.start_system_thread(c_key)

    def stop_device(self, device_id, device_name):
        self._workers[str(device_id)].running = False
        del self._workers[str(device_id)]
        self._logger.info(f"Stopped device {device_name}")
        return True

    def get_running_devices(self):
        running_devices = self._api.get_running_threads()
        output = {}
        if running_devices:
            for c_device in running_devices["devices"]:
                device_id = c_device["id"]
                del c_device["id"]
                output[device_id] = c_device
        return output

    def set_version(self):
        self._api.send_version_string(config("VERSION"))

    def validate_module_config_module(self, module_name):
        config = self._module_config[module_name]
        exec(f"from src.modules.{config['filename']} import {config['classname']}", globals())
        self._imported_modules.append(module_name)
        exec(f"is_valid = {config['classname']}.check_module_configuration()", globals())
        return is_valid

    def set_modules(self, validate_settings=True):
        output = []
        for module_name in self._modules.get_whole_file():
            if validate_settings is False or self.validate_module_config_module(module_name):
                c_classname = self._modules.read_config_file(module_name)['classname']
                exec(f"settings_signature, settings_fields = {c_classname}.config_template().serialize()", globals())
                output.append({
                    "id": module_name,
                    "config_signature": settings_signature,
                    "config_fields": settings_fields
                })
            else:
                self._logger.critical(f"{module_name} is not configured correctly!")
        self._api.send_known_modules(output)
