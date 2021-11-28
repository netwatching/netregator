import threading
import time
from src.device import Device
from src.module_data import ModuleData
from src.device_data import DeviceData


class Module(threading.Thread):
    def __init__(self, ip: str, timeout: int, *args, **kwargs):
        deviceCreated = False
        self.__data = DeviceData()
        self.timeout=timeout
        self.ip=ip
        super().__init__(*args, **kwargs)
        self._stop = threading.Event()

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data: ModuleData):
        self.__data.add_module_data(data)

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout):
        self.__timeout = int(timeout)

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ip):
        self.__ip = ip

    def is_stopped(self):
        return self._stop.is_set()

    def stop(self):
        self._stop.set()

    def clear_data(self):
        self.__data = DeviceData()

    def run(self):
        while not self.is_stopped():
            #timestamp = time.time()
            #worker_data: ModuleData = self.worker()
            #if "timestamp" in workerdict:
            #    timestamp = workerdict["timestamp"]
            #for key in workerdict:
            #    if key != "timestamp":
            #        self.data = {"timestamp": timestamp, "key": key, "value": workerdict[key]}
            #static_data = worker_data.static_data
            #live_data = worker_data.live_data
            self.data = self.worker()

            time.sleep(int(self.timeout))

    def worker(self):
        return ModuleData({"Error": f"Worker class of Type {self.ip} not yet implemented!"}, {}, {})