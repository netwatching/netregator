import threading
import time
from src.io import Config
import json


class Device(threading.Thread):

    def __init__(self, id, name: str, ip: str, device_type: str, timeout: int, modules: dict, *args, **kwargs):
        self._module_config = Config("./src/config/modules.json").get_whole_file()
        self._imported_modules = []
        self._workers = {}
        self.__data = {}
        self.name = name
        self.id = id
        self.ip = ip
        self.device_type = device_type
        self.timeout = timeout
        self.modules = modules
        self.running = True
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
        c_data = self.__data
        self.__data = {}
        return c_data

    @data.setter
    def data(self, module_name):
        module_data = self._workers[module_name].data
        if module_data:
            if not module_name in self.__data:
                self.__data[module_name] = list()
            self.__data[module_name] = self.__data[module_name] + module_data

    def run(self):
        self.start_modules()
        time.sleep(5)
        while True:
            self.get_data()
            time.sleep(5)
        # while self.running:
        #    print(f"WORKING! - {self.name}")
        #    time.sleep(100)

    def start_modules(self):
        for c_module in self.modules:
            if c_module["name"] not in self._imported_modules:
                self.import_module(c_module["name"])
            # code = f"global c_worker;c_worker = {self._module_config[c_module['name']]['classname']}(deviceid={self.id},devicetype='{self.device_type}',devicename='{self.name}',deviceip='{self.ip}', devicetimeout={self.timeout}, devicemodules={self.modules})"
            code = f"global c_worker;c_worker = {self._module_config[c_module['name']]['classname']}(ip='{self.ip}', timeout={self.timeout})"
            print(code)
            exec(code, globals())
            self._workers[c_module["name"]] = c_worker
            c_worker.start()

    def check_modules(self):
        for c_module in self.modules:
            pass


    def import_module(self, module_name):
        config = self._module_config[module_name]
        exec(f"from src.modules.{config['filename']} import {config['classname']}", globals())
        self._imported_modules.append(module_name)
        print(f"Successfully imported module {module_name}")

    def get_data(self):
        for c_module in self._workers:
            self.data = c_module
