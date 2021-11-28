from src.modules.module import Module
from src.device import Device
from src.module_data import ModuleData
import src.modules.helpers.snmp as snmp


class SNMP(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)
        self.__ds = snmp.DataSources(snmp.SNMP("HTL-Villach", ip, 161))

    def worker(self):
        # return ModuleData(static_data={
        #     "ipAddr": {
        #         "127.0.0.1": {
        #             "Addr": "127.0.0.1",
        #             "netmask": "255.255.255.255"
        #         },
        #         "169.65.2.5": {
        #             "Addr": "169.65.2.5",
        #             "netmask": "255.255.255.0"
        #         }
        #     },
        #     "interface": {
        #         "1": {
        #             "ifIndex": 1,
        #             "ifDescr": "LinkAggregate1",
        #             "ifAdminStatus": "up"
        #         },
        #         "52": {
        #             "ifIndex": 52,
        #             "ifDescr": "LinkAggregate52",
        #             "ifAdminStatus": "down"
        #         }
        #     },
        #     "hostname": "ciscoSW1"
        # }, live_data={}, events={})
        data = {}

        data.update(self.__ds.get_hostname())
        data.update(self.__ds.get_object_id())
        data.update(self.__ds.get_uptime())
        data.update(self.__ds.get_description())
        data.update(self.__ds.get_contact())
        data.update(self.__ds.get_name())
        data.update(self.__ds.get_services())
        data.update(self.__ds.get_interfaces())
        data.update(self.__ds.get_ip_addresses())
        # TODO: add other DataSource functions above

        # print(data)  # TODO: logging class
        return ModuleData(static_data=data, live_data={}, events={})
