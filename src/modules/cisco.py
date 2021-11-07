from src.modules.module import Module
from src.device import Device
import src.modules.helpers.snmp as snmp


class Cisco(Module):
    def __init__(self, device: Device = None, *args, **kwargs):
        super().__init__(device, *args, **kwargs)
        self.__ds = snmp.DataSources(snmp.SNMP("snmp_rw", self.device.ip, 161))

    def worker(self):
        data = {}

        data.update(self.__ds.get_hostname())
        data.update(self.__ds.get_object_id())
        data.update(self.__ds.get_uptime())
        data.update(self.__ds.get_description())
        data.update(self.__ds.get_contact())
        data.update(self.__ds.get_name())
        data.update(self.__ds.get_services())
        data.update(self.__ds.get_interfaces())
        # TODO: add other DataSource functions above

        print(data)  # TODO: logging class
        return data
