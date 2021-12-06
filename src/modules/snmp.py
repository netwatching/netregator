from src.modules.module import Module
from src.device import Device
from src.module_data import ModuleData
import src.modules.helpers.snmp as snmp


class SNMP(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)
        self.__ds = snmp.DataSources(snmp.SNMP("HTL-Villach", ip, 161))

    def worker(self):
        # return ModuleData(static_data={}, live_data={}, events={})
        data = {}

        # data.update(self.__ds.get_hostname())
        # data.update(self.__ds.get_object_id())
        # data.update(self.__ds.get_uptime())
        # data.update(self.__ds.get_description())
        # data.update(self.__ds.get_contact())
        # data.update(self.__ds.get_name())
        data.update(self.__ds.get_system_data())
        data.update(self.__ds.get_services())
        data.update(self.__ds.get_interfaces())
        data.update(self.__ds.get_ip_data())
        data.update(self.__ds.get_ip_addresses())
        # TODO: add other DataSource functions above

        # print(data)  # TODO: logging class
        return ModuleData(static_data=data, live_data={}, events={})
