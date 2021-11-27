from src.modules.module import Module
from src.device import Device
from pyzabbix.api import ZabbixAPI
from decouple import config

class ZabbixDevice:
    def __init__(self, hostid: str = None, hostname: str = None, name: str = None, problem: str = None, timestamp: float = None, severity: str = None, tag: list = None):
        self.hostid = hostid
        self.hostname = hostname
        self.name = name
        self.problem = problem
        self.timestamp = timestamp
        self.severity = severity
        self.tag = tag

    @property
    def hostid(self):
        return self.__hostid

    @hostid.setter
    def hostid(self, host_id):
        self.__hostid = host_id

    @property
    def hostname(self):
        return self.__hostname

    @hostname.setter
    def hostname(self, host_name):
        self.__hostname = host_name

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def tag(self):
        return self.__tag

    @tag.setter
    def tag(self, host_tag):
        self.__tag = host_tag

    @property
    def problem(self):
        return self.__problem

    @problem.setter
    def problem(self, problem):
        self.__problem = problem

    @property
    def severity(self):
        return self.__severity

    @severity.setter
    def severity(self, severity):
        self.__severity = severity

    @property
    def timestamp(self):
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self.__timestamp = timestamp

    def serialize(self):
        output = {"id": self.hostid, "hostname": self.hostname, "name": self.name, "timestamp": self.timestamp, "severity": self.severity,
                  "tag": self.tag, "problem": self.problem}
        return output


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
        return hosts

    def get_infos(self, hosts):
        zabbix_devices = []
        for host in hosts:
            z_device = ZabbixDevice()
            problem_obj = self.__connection.problem.get(hostids=host['hostid'], selectHosts='extend')
            if problem_obj:
                for obj in problem_obj:
                    z_device.hostid = host["hostid"]
                    z_device.hostname = host["host"]
                    z_device.name = host["name"]
                    z_device.timestamp = obj["clock"]
                    z_device.severity = obj["severity"]
                    z_device.problem = obj["name"]

                tag_obj = self.__connection.host.get(hostids=host['hostid'], selectTags="extend")
                for obj in tag_obj:
                    tags = obj['tags']
                    z_tags = []
                    for t in tags:
                        z_tags.append(t['tag'])
                    z_device.tag = z_tags
                    #print(z_device.serialize())
                    zabbix_devices.append(z_device.serialize())

        return zabbix_devices


    def worker(self):
        hosts = self.get_hosts()
        problems = self.get_infos(hosts)
        #print(problems)
        return {"problems": problems}