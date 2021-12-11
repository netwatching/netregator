import threading
import time
from src.io import Config
import json
from src.utilities import Utilities
from src.device_data import DeviceData


class Device(threading.Thread):

    def __init__(self, id, name: str, ip: str, device_type: str, timeout: int, modules: dict, *args, **kwargs):
        self._module_config = Config("./src/config/modules.json").get_whole_file()
        self._imported_modules = []
        self._workers = {}
        self.__data = DeviceData()
        self.name = name
        self.id = id
        self.ip = ip
        self.device_type = device_type
        self.timeout = timeout
        self.modules = modules
        self.running = True
        self._utilities = Utilities()
        super().__init__(*args, **kwargs)

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ip):
        self.__ip = ip

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def device_type(self):
        return self.__device_type

    @device_type.setter
    def device_type(self, type):
        self.__device_type = type

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout: int):
        self.__timeout = int(timeout)

    @property
    def modules(self):
        return self.__modules

    @modules.setter
    def modules(self, modules: dict):
        self.__modules = modules

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, is_running: bool):
        self.__running = is_running

    @property
    def data(self):
        return self.__data.serialize(), self.__data.external_events

    @data.setter
    def data(self, module_name):
        module_data = self._workers[module_name].data
        self.__data.add_module_data(module_data)
        #(module_data)
        #if module_data:
        #    self.__data["static_data"].update(module_data.static_data)
        #    self.__data["live_data"].update(module_data.live_data)
        #    self.__data["events"].update(self.__data["events"])

    def run(self):
        while self.running:
            self.get_data()
            self.check_modules()
            time.sleep(5)
        worker_names = list(self._workers.keys())
        for c_worker in worker_names:
            self.stop_module(c_worker)

    def start_module(self, module):
        if module["name"] not in self._imported_modules:
            self.import_module(module["name"])
        code = f"global c_worker;c_worker = {self._module_config[module['name']]['classname']}(ip='{self.ip}', timeout={self.timeout}, config={module['config']})"
        exec(code, globals())
        self._workers[module["name"]] = c_worker
        c_worker.start()
        print(f"Started module {module['name']}")

    def check_modules(self):
        # start modules
        module_api_out = {}
        for c_module in self.modules:
            module_api_out[c_module["name"]] = {"config": c_module["config"]}
            if c_module["name"] not in self._workers:
                self.start_module(c_module)
            if not self._workers[c_module['name']].is_running() or not self._workers[c_module['name']].is_alive():
                self.start_module(c_module)

        # stop modules
        modules_to_stop = self._utilities.compare_list(self._workers.keys(), module_api_out.keys())
        for c_module in modules_to_stop:
            print(f"Stopped module {c_module}")
            self.stop_module(c_module)

        # update modules
        for c_module_name, c_module_worker in self._workers.items():
            c_module_worker.timeout = self.timeout
            c_module_worker.config = module_api_out[c_module_name]["config"]
            # TODO: Config timeout nutzen statt Device


    def import_module(self, module_name):
        config = self._module_config[module_name]
        exec(f"from src.modules.{config['filename']} import {config['classname']}", globals())
        self._imported_modules.append(module_name)
        print(f"Successfully imported module {module_name}")

    def stop_module(self, module_name):
        self._workers[module_name].stop()
        self._workers.pop(module_name)
        print(f"Stopped module {module_name}")

    def get_data(self):
        for c_module in self._workers:
            self.data = c_module
            self._workers[c_module].clear_data()

    def clear_data(self):
        self.__data = DeviceData()
