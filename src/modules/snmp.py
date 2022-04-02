from src.modules.module import Module
from src.device import Device
from src.module_data import ModuleData, OutputType, Event, EventSeverity, LiveData
from src.utilities import Utilities
import src.modules.helpers.snmp as snmp
from src.settings import Settings, SettingsItem, SettingsItemType


class SNMP(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)
        self.ip = ip
        self.__update_config()
        self._logger = Utilities.setup_logger()
        self.__ds = snmp.DataSources(snmp.SNMP(self.community_string, ip, self.port))

    def __update_config(self):
        self.community_string = self.get_config_value("SNMP_COMMUNITY")
        self.port = self.get_config_value("SNMP_PORT")

    @staticmethod
    def config_template():
        settings = Settings(default_timeout=30*60)
        settings.add(SettingsItem(SettingsItemType.STRING, "SNMP_COMMUNITY", "community string", "snmp_rw"))
        settings.add(SettingsItem(SettingsItemType.NUMBER, "SNMP_PORT", "port", 161))
        return settings

    def worker(self):
        # self._logger.info(f"starting to fetch SNMP information from device with IP: {self.ip}")
        # return ModuleData(static_data={}, live_data={}, events={})

        #return ModuleData({}, [], [Event("successfully sent", EventSeverity.DEBUG)], OutputType.DEFAULT)
        static_data = {}
        live_data = []

        static_data.update(self.__ds.get_system_data())
        static_data.update(self.__ds.get_services())
        interfaces_static, interfaces_live = self.__ds.get_interfaces()
        static_data.update({"network_interfaces": interfaces_static})
        for key, val in interfaces_live.items():
            for i_key, i_val in val.items():
                live_data.append(LiveData(key+i_key, float(i_val)))
        # data.update(self.__ds.get_ip_data())
        static_data.update(self.__ds.get_ip_addresses())
        # TODO: add other DataSource functions above

        # self._logger.spam(data)
        return ModuleData(static_data=static_data, live_data=live_data, events={})
