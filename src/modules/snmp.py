from src.modules.module import Module
from src.device import Device
from src.module_data import ModuleData
from src.utilities import Utilities
import src.modules.helpers.snmp as snmp
from src.settings import Settings, SettingsItem, SettingsItemType


class SNMP(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)
        self.ip = ip
        self.settings = {
            "community_string": "HTL-Villach",
            "c_str_2": "snmp_rw",  # TODO: replace by proper setting
            "snmp_port": 161
        }
        self._logger = Utilities.setup_logger()
        self.__ds = snmp.DataSources(snmp.SNMP(self.settings["community_string"], ip, self.settings["snmp_port"]))

    @staticmethod
    def config_template():
        settings = Settings(default_timeout=30*60)
        return settings

    def worker(self):
        # self._logger.info(f"starting to fetch SNMP information from device with IP: {self.ip}")
        # return ModuleData(static_data={}, live_data={}, events={})
        data = {}

        try:
            data.update(self.__ds.get_system_data())
            data.update(self.__ds.get_services())
            data.update(self.__ds.get_interfaces())
            # data.update(self.__ds.get_ip_data())
            data.update(self.__ds.get_ip_addresses())
            # TODO: add other DataSource functions above
        except Exception:
            self.__ds = snmp.DataSources(snmp.SNMP(self.settings["c_str_2"], self.ip, self.settings["snmp_port"]))
            data.update(self.__ds.get_system_data())
            data.update(self.__ds.get_services())
            data.update(self.__ds.get_interfaces())
            # data.update(self.__ds.get_ip_data())
            data.update(self.__ds.get_ip_addresses())
            # TODO: add other DataSource functions above

        # self._logger.spam(data)
        return ModuleData(static_data=data, live_data={}, events={})
