from src.modules.module import Module
from decouple import config
from src.module_data import ModuleData, OutputType, Event, EventSeverity
from src.modules.helpers.s350_ssh_vlan import Vlan
from src.settings import Settings, SettingsItem, SettingsItemType
import sys
import time
import napalm
import os
import json


class SSH(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)
        self.ip = ip
        self.__update_config()

    def __update_config(self):
        self.username = self.get_config_value("SSH_USERNAME")
        self.password = self.get_config_value("SSH_PASSWORD")
        self.secret = self.get_config_value("SSH_ENABLE_SECRET")
        self.dev_type = self.get_config_value("SSH_DEVICE_TYPE")
        self.dev_creds = {
            'hostname': self.ip,
            'username': self.username,
            'password': self.password,
        }
        if self.secret:
            self.dev_creds['optional_args'] = {'secret': self.secret}
        else:
            self.dev_creds['optional_args'] = {'force_no_enable': True}

    def __create_connection(self):
        self.__update_config()
        print(self.dev_type)
        driver = napalm.get_network_driver(self.dev_type)
        self.conn = driver(**self.dev_creds)
        self.conn.open()

    def get_lldp_infos(self):
        self.__create_connection()
        interface_output = self.conn.get_interfaces()
        lldp_output = self.conn.get_lldp_neighbors_detail()
        neighbors = {}

        for portname, data in lldp_output.items():
            neighbor = {
                portname: [{
                    "local_mac": interface_output[portname]["mac_address"],
                    "local_port": portname,
                    "remote_host": lldp_output[portname][0]["remote_system_name"],
                    "remote_chassis_id": lldp_output[portname][0]["remote_chassis_id"],
                    "remote_port": lldp_output[portname][0]["remote_port"],
                    "remote_system_description": lldp_output[portname][0]["remote_system_description"],
                    "remote_system_capability": lldp_output[portname][0]["remote_system_capab"][-1]
                }]
            }
            neighbors.update(neighbor)
        self.conn.close()
        return {"neighbors": neighbors}

    def get_vlan_infos(self):
        self.__update_config()
        vlan_data = Vlan(self.dev_creds).get_vlan_data()
        return {"vlan": vlan_data}

    @staticmethod
    def config_template():
        settings = Settings(default_timeout=30*60)
        settings.add(SettingsItem(SettingsItemType.STRING, "SSH_USERNAME", "username", "NetWatch"))
        settings.add(SettingsItem(SettingsItemType.STRING, "SSH_PASSWORD", "password", "!NetWatch2021?"))
        settings.add(SettingsItem(SettingsItemType.STRING, "SSH_ENABLE_SECRET", "enable secret", "",
                                  settings_required=False))  # HTL-Villach
        settings.add(SettingsItem(SettingsItemType.ENUM, "SSH_DEVICE_TYPE", "device type", "s350", ["s350", "nxos"]))
        return settings

    def worker(self):
        # return ModuleData({}, [], [Event("successfully sent", EventSeverity.DEBUG)], OutputType.DEFAULT)
        data = {}
        data.update(self.get_lldp_infos())
        data.update(self.get_vlan_infos())
        return ModuleData(self.get_lldp_infos(), [], {}, OutputType.DEFAULT)

