import threading
import time
from src.device import Device


class Module(threading.Thread):
    def __init__(self, device: Device=None, *args, **kwargs):
        self.__data = []
        if(device is not None):
            self.device = device
        else:
            if "deviceid" in kwargs and "devicename" in kwargs and "deviceip" in kwargs and "devicetype" in kwargs:
                self.device = Device(id=kwargs["deviceid"], name=kwargs["devicename"], ip=kwargs["deviceip"], type=kwargs["devicetype"])
            else:
                self.device = None

        customkwargs = kwargs
        del customkwargs["devicename"]
        del customkwargs["deviceid"]
        del customkwargs["deviceip"]
        del customkwargs["devicetype"]
        super().__init__(*args, **customkwargs)
        self._stop = threading.Event()

    @property
    def data(self):
        cData = self.__data
        self.__data = []
        return cData

    @data.setter
    def data(self, data):
        self.__data.append(data)

    @property
    def device(self):
        return self.__device

    @device.setter
    def device(self, device):
        self.__device = device

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
                if key is not "timestamp":
                    self.data = {"timestamp": timestamp, "key": key, "value": workerdict[key]}
            time.sleep(1)

    def worker(self):
        return {"Error": f"Worker class of Type {self.device.type} not yet implemented!"}