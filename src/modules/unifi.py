from src.modules.module import Module
from src.device import Device
from src.module_data import ModuleData, OutputType
from unificontrol import UnifiClient
from decouple import config


class UnifiLLDP:
    def __init__(self, chassis_id: str = None, remote_host: str = None, is_wired: str = None,
                 local_port_idx: int = None, port_id: str = None):
        self.chassis_id = chassis_id
        self.remote_host = remote_host
        self.is_wired = is_wired
        self.local_port_idx = local_port_idx
        self.port_id = port_id

    def serialize(self):
        return {"local_port": self.local_port_idx, "remote_host": self.remote_host,
                "remote_chassis_id": self.chassis_id,
                "remote_port": self.port_id, "remote_system_description": "", "remote_system_capability": "",
                "is_wired": self.is_wired}


class UnifiVLAN:
    def __init__(self, local_port_name: str = None, vlan_name: str = None, vlan_id: int = None,
                 admin_status: str = None):
        self.local_port_name = local_port_name
        self.vlan_name = vlan_name
        self.vlan_id = vlan_id
        self.admin_status = admin_status

    def serialize(self):
        return {"id": self.vlan_id, "name": self.vlan_name}


class UnifiDevice:
    def __init__(self, ip: str = None):
        self.ip = ip
        self.data = {}

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ipaddr):
        self.__ip = ipaddr


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

    def _get_network_obj(self, network, key):
        for network_obj in network:
            if network_obj["_id"] == key:
                return network_obj

    def _get_portconfig_obj(self, portconfig, key):
        for portconfig_obj in portconfig:
            if portconfig_obj["_id"] == key:
                return portconfig_obj

    def get_lldp_data(self):
        lldp_data = {}
        mac = ""
        hostname = ""
        portname = ""

        device = UnifiDevice(ip=self.ip)
        all_devices = self.connection.list_devices()
        for obj_ in all_devices:
            if obj_["ip"] == self.ip:
                mac = obj_["mac"]

        all_clients = self.connection.list_clients()
        devices = self.connection.list_devices(device_mac=mac)
        for device_data in devices:
            lldp_device = device_data["lldp_table"]
            lldp_list = []
            for i in range(len(lldp_device)):
                for clients in all_clients:
                    if clients["mac"] == lldp_device[i]["chassis_id"]:
                        if "hostname" in clients:
                            hostname = clients["hostname"]


                        lldp = UnifiLLDP(chassis_id=lldp_device[i]["chassis_id"], remote_host=hostname,
                                         is_wired=lldp_device[i]["is_wired"],
                                         local_port_idx=lldp_device[i]["local_port_idx"],
                                         port_id=lldp_device[i]["port_id"])
                        lldp_list.append(lldp.serialize())

            output_data = {}
            for c_vlan_data in lldp_list:
                if c_vlan_data["local_port"] not in output_data:
                    output_data[c_vlan_data["local_port"]] = []
                output_data[c_vlan_data["local_port"]].append(c_vlan_data)

            return output_data

    def get_vlan_data(self):
        vlan_data_devices = {}

        device = UnifiDevice(ip=self.ip)
        alldevices = self.connection.list_devices()
        for obj in alldevices:
            if obj["ip"] == self.ip:
                mac = obj["mac"]
                break

        portconf = self.connection.list_portconf()
        networks = self.connection.list_networkconf()

        vlandevice = self.connection.list_devices(mac)
        for devices in vlandevice:
            port_table = devices["port_table"]
            for port in port_table:
                port_idx = port["port_idx"]
                port_status = port["name"]

                portconf_obj = self._get_portconfig_obj(portconf, port["portconf_id"])
                admin_status = "down" if port_status == "Disabled" else "up"

                if "native_networkconf_id" in portconf_obj:
                    network_obj = self._get_network_obj(networks, portconf_obj["native_networkconf_id"])
                    if network_obj["_id"] == portconf_obj["native_networkconf_id"]:
                        vlan = UnifiVLAN(local_port_name=port_idx, vlan_name=network_obj["name"],
                                         vlan_id=network_obj["vlan"], admin_status=admin_status)
                else:
                    vlan = UnifiVLAN(local_port_name=port_idx, vlan_name="Default",
                                     vlan_id=-1, admin_status=admin_status)

                vlan_dict = vlan.serialize()

                vlan_list = [vlan_dict]
                port_dict = {"vlans": vlan_list, "admin_status": admin_status}
                device.data[port_idx] = port_dict

            vlan_data_devices = device.data
        return vlan_data_devices


class LLDP(UnifiAPI):
    def __init__(self, ip: str = None, *args, **kwargs):
        super().__init__(ip, *args, **kwargs)

    def worker(self):
        lldp = self.get_lldp_data()
        return ModuleData({"lldp": lldp}, [], {}, OutputType.DEFAULT)


class VLAN(UnifiAPI):
    def __init__(self, ip: str = None, *args, **kwargs):
        super().__init__(ip, *args, **kwargs)

    def worker(self):
        vlan = self.get_vlan_data()
        return ModuleData(vlan, [], {}, OutputType.DEFAULT)
