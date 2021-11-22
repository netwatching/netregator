import threading
import time
from src.device import Device


class Module(threading.Thread):
    def __init__(self, ip: str, timeout: int, *args, **kwargs):
        deviceCreated = False
        self.__data = []
        self.timeout=timeout
        self.ip=ip
        super().__init__(*args, **kwargs)
        self._stop = threading.Event()

    @property
    def data(self):
        c_data = self.__data
        self.__data = []
        return c_data

    @data.setter
    def data(self, data):
        self.__data.append(data)

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

    def run(self):
        while not self.is_stopped():
            timestamp = time.time()
            workerdict = self.worker()
            if "timestamp" in workerdict:
                timestamp = workerdict["timestamp"]
            for key in workerdict:
                if key != "timestamp":
                    self.data = {"timestamp": timestamp, "key": key, "value": workerdict[key]}
            time.sleep(int(self.timeout))

    def worker(self):
        return {"Error": f"Worker class of Type {self.device.type} not yet implemented!"}