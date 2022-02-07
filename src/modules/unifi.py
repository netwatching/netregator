from src.modules.module import Module
from src.device import Device
from src.module_data import ModuleData, OutputType
from unificontrol import UnifiClient
from decouple import config


class UnifiLLDP:
    def __init__(self, chassis_id: str = None, remote_host: str = None, is_wired: str = None,
                 local_port_idx: int = None,
                 local_port_name: str = None, port_id: str = None):
        self.chassis_id = chassis_id
        self.remote_host = remote_host
        self.is_wired = is_wired
        self.local_port_idx = local_port_idx
        self.local_port_name = local_port_name
        self.port_id = port_id

    def serialize(self):
        return {"local_port": self.local_port_name, "remote_host": self.remote_host,
                "remote_chassis_id": self.chassis_id,
                "remote_port": self.port_id, "remote_system_description": "", "remote_system_capability": "",
                "is_wired": self.is_wired}


class UnifiDevice:
    def __init__(self, ip: str = None):
        self.ip = ip
        self.data = []

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ipaddr):
        self.__ip = ipaddr

    def serialize(self):
        out = []
        for lldp in self.data:
            out.append(lldp.serialize())
        return {self.ip: out}


class UnifiAPI(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)

        self.host = config("UNIFI_HOSTNAME")
        # self.user = self.config["username"]
        self.user = config("UNIFI_USERNAME")
        # self.password = self.config["password"]
        self.password = config("UNIFI_PASSWORD")
        self.connection = self.__create_connection()

    def __create_connection(self):
        return UnifiClient(host=self.host, username=self.user, password=self.password)

    def get_lldp_data(self):
        lldp_data = {}
        mac = ""
        hostname = ""

        device = UnifiDevice(ip=self.ip)
        alldevices = self.connection.list_devices()
        for obj in alldevices:
            if obj["ip"] == self.ip:
                print(obj["mac"])
                mac = obj["mac"]

        allclients = self.connection.list_clients()

        lldpdevice = self.connection.list_devices(device_mac=mac)
        for obj in lldpdevice:
            for client in allclients:
                if client["mac"] == obj["lldp_table"][0]["chassis_id"]:
                    hostname = client["hostname"]

            lldp = UnifiLLDP(chassis_id=obj["lldp_table"][0]["chassis_id"], remote_host=hostname,
                             is_wired=obj["lldp_table"][0]["is_wired"],
                             local_port_idx=obj["lldp_table"][0]["local_port_idx"],
                             local_port_name=obj["lldp_table"][0]["is_wired"],
                             port_id=obj["lldp_table"][0]["port_id"])

            device.data.append(lldp)

            if not self.ip in lldp_data:
                lldp_data[self.ip] = []
            lldp_data.update(device.serialize())
        return lldp_data


class LLDP(UnifiAPI):
    def __init__(self, ip: str = None, *args, **kwargs):
        super().__init__(ip, *args, **kwargs)

    def worker(self):
        lldp = self.get_lldp_data()
        return ModuleData(lldp, [], {}, OutputType.DEFAULT)
