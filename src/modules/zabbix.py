from src.modules.module import Module
from src.device import Device
from pyzabbix.api import ZabbixAPI
from decouple import config
from src.module_data import ModuleData, OutputType


class ZabbixProblems:
    def __init__(self, problem: str = None, timestamp: float = None, severity: str = None):
        self.problem = problem
        self.timestamp = timestamp
        self.severity = severity

    def serialize(self):
        return {"timestamp": self.timestamp, "severity": self.severity, "data": self.problem}


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


class Problems(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)
        self.url = f"https://{ip}"
        self.user = config("ZABBIX_USERNAME")
        self.password = config("ZABBIX_PASSWORD")
        self.__connection = self.__create_connection()

    def __create_connection(self):
        return ZabbixAPI(url=self.url, user=self.user, password=self.password)

    def get_hosts(self):
        hosts = self.__connection.host.get(output=["hostid", "host", "name"])
        print(hosts)
        return hosts

    def get_infos(self, hosts):
        zabbix_devices = {}
        for host in hosts:
            z_device = ZabbixDevice(hostname=host["host"])
            problem_obj = self.__connection.problem.get(hostids=host['hostid'], selectHosts='extend')
            if problem_obj:
                for obj in problem_obj:
                    z_problem = ZabbixProblems(problem=obj["name"], severity=obj["severity"], timestamp=obj["clock"])
                    z_device.problems.append(z_problem)

                    if not host["host"] in zabbix_devices:
                        zabbix_devices[host["host"]] = []
                    zabbix_devices.update(z_device.serialize())
        return zabbix_devices

    def worker(self):
        hosts = self.get_hosts()
        problems = self.get_infos(hosts)
        print(problems)
        return ModuleData({}, {}, problems, OutputType.EXTERNAL_DATA_SOURCES)

    @staticmethod
    def check_module_configuration():
        if config("ZABBIX_USERNAME") and config("ZABBIX_PASSWORD"):
            return True
        else:
            return False
