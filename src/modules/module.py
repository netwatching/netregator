import datetime
import threading
import time
from src.module_data import ModuleData
from src.device_data import DeviceData
from src.settings import Settings, SettingsItem, SettingsItemType
from src.utilities import Utilities


class Module(threading.Thread):
    def __init__(self, ip: str, timeout: int, config: dict, *args, **kwargs):
        self._logger = Utilities.setup_logger(ip)
        self.__data = DeviceData()
        self.timeout = timeout
        self.ip = ip
        self.config_signature, self.default_config = self.__class__.config_template().serialize()
        # print(self.default_config)
        self.config = config
        self.last_updated = datetime.datetime.now()
        super().__init__(*args, **kwargs)
        self.__is_running = True

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, data: dict):
        if not data:
            self.__config = self.default_config
        else:
            self.__config = data

    @property
    def data(self):
        self.last_updated = datetime.datetime.now()
        return self.__data

    @data.setter
    def data(self, data: ModuleData):
        self.__data.add_module_data(data)

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout):
        self.last_updated = datetime.datetime.now()
        self.__timeout = int(timeout)

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ip):
        self.last_updated = datetime.datetime.now()
        self.__ip = ip

    def is_running(self):
        return self.__is_running

    def stop(self):
        self.__is_running = False

    def clear_data(self):
        self.last_updated = datetime.datetime.now()
        self.__data = DeviceData()

    @staticmethod
    def config_template():
        settings = Settings()
        return settings

    def run(self):
        while self.is_running():
            if (datetime.datetime.now() - self.last_updated) > datetime.timedelta(minutes=5):
                self.stop()
            self.data = self.worker()
            if "timeout" in self.config:
                c_timeout = self.config["timeout"]
            else:
                c_timeout = self.timeout
            time.sleep(int(c_timeout))

    def get_config_value(self, identifier):
        if identifier in self.config:
            return self.config[identifier]
        else:
            return None

    @staticmethod
    def check_module_configuration():
        return True

    def worker(self) -> ModuleData:
        return ModuleData({"Error": f"Worker class of Type {self.ip} not yet implemented!"}, [], {})
