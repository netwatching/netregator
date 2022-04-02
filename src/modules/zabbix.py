import math

from src.modules.module import Module
from src.device import Device
from pyzabbix.api import ZabbixAPI
from decouple import config
from src.module_data import ModuleData, OutputType, LiveData
import time
from enum import Enum
from src.settings import Settings, SettingsItem, SettingsItemType


class ZabbixDataType(Enum):
    PROBLEMS = 0
    EVENTS = 1


class ZabbixProblems:
    def __init__(self, problem: str = None, timestamp: float = None, severity: int = None):
        self.problem = problem
        self.timestamp = timestamp
        self.severity = severity

    def serialize(self):
        return {"timestamp": self.timestamp, "severity": self.severity, "information": self.problem}


class ZabbixDevice:
    def __init__(self, hostname: str = None):
        self.hostname = hostname
        self.problems = []

    @property
    def hostname(self):
        return self.__hostname

    @hostname.setter
    def hostname(self, host_name):
        self.__hostname = host_name

    def serialize(self):
        out = []
        for c_problem in self.problems:
            out.append(c_problem.serialize())
        return {self.hostname: out}


class Zabbix(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)
        self.url = f"https://{ip}"
        # self.user = self.config["username"]
        self.user = self.get_config_value("ZABBIX_USERNAME")
        # self.password = self.config["password"]
        self.password = self.get_config_value("ZABBIX_PASSWORD")
        self.connection = self.__create_connection()

    def __create_connection(self):
        return ZabbixAPI(url=self.url, user=self.user, password=self.password)

    def get_infos(self, hosts, zabbix_data_type: ZabbixDataType):
        zabbix_devices = {}
        for host in hosts:
            z_device = ZabbixDevice(hostname=host["host"])
            data_obj = None
            if zabbix_data_type == ZabbixDataType.PROBLEMS:
                data_obj = self.connection.problem.get(hostids=host['hostid'], selectHosts='extend')
            elif zabbix_data_type == ZabbixDataType.EVENTS:
                data_obj = self.connection.event.get(hostids=host['hostid'], time_from=time.time() - 86400)  # 86400
            if data_obj:
                for obj in data_obj:
                    if zabbix_data_type == ZabbixDataType.EVENTS:
                        c_severity = math.ceil((int(obj["severity"]) + 1)/2)
                    else:
                        c_severity = math.ceil((int(obj["severity"]) + 5)/2)
                    c_problem = str.replace(obj["name"], '"', '')
                    z_problem = ZabbixProblems(problem=c_problem, severity=c_severity, timestamp=obj["clock"])
                    z_device.problems.append(z_problem)

                    if not host["host"] in zabbix_devices:
                        zabbix_devices[host["host"]] = []
                    zabbix_devices.update(z_device.serialize())
        return zabbix_devices

    def get_hosts(self):
        hosts = self.connection.host.get(output=["hostid", "host", "name"])
        return hosts

    @staticmethod
    def config_template():
        settings = Settings(default_timeout=30*60)
        settings.add(SettingsItem(SettingsItemType.STRING, "ZABBIX_USERNAME", "username", ""))
        settings.add(SettingsItem(SettingsItemType.STRING, "ZABBIX_PASSWORD", "password", ""))
        return settings

    @staticmethod
    def check_module_configuration():
        # if config("ZABBIX_USERNAME") and config("ZABBIX_PASSWORD"):
        #     return True
        # else:
        #     return False
        return True


class Problems(Zabbix):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)

    def worker(self):
        hosts = self.get_hosts()
        problems = self.get_infos(hosts, ZabbixDataType.PROBLEMS)
        return ModuleData({}, [], problems, OutputType.EXTERNAL_DATA_SOURCES)


class Events(Zabbix):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)

    def worker(self):
        hosts = self.get_hosts()
        events = self.get_infos(hosts, ZabbixDataType.EVENTS)
        return ModuleData({}, [], events,
                          OutputType.EXTERNAL_DATA_SOURCES)

    @staticmethod
    def config_template():
        settings = Settings(default_timeout=60)
        settings.add(SettingsItem(settings_id="username", settings_title="Zabbix Username",
                                  settings_type=SettingsItemType.STRING,
                                  settings_default_value="user"))
        settings.add(SettingsItem(settings_id="password", settings_title="Zabbix Password",
                                  settings_type=SettingsItemType.STRING,
                                  settings_default_value="password"))
        return settings
