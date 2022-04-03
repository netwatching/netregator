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
            'optional_args': {'transport': self.get_config_value("SSH_TRANSPORT_PROTOCOL")}
        }
        if self.secret:
            self.dev_creds['optional_args']["secret"] = self.secret
        else:
            self.dev_creds['optional_args']['force_no_enable'] = True

    def __create_connection(self):
        self.__update_config()  # the config needs to be updated in case the user changes the config while the program runs
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
        self._logger.spam(neighbors)
        return {"neighbors": neighbors}

    @staticmethod
    def reformat_vlan_data(vlans):
        vlan_results = []
        ports = []  # memorize all ports already in the output variable
        for vlan_id, vlan_data in vlans.items():
            vlan_name = vlan_data["name"]
            interfaces = vlan_data["interfaces"]
            for interface in interfaces:
                if interface in ports:  # update an existing port in the out var
                    port_index = ports.index(interface)
                    vlan_results[port_index]["vlans"].append({"id": vlan_id, "name": vlan_name})
                else:  # add a new port to the output var
                    vlan_results.append({
                        "port": interface,
                        "vlans": [{"id": vlan_id, "name": vlan_name}]
                    })
                    ports.append(interface)
        return vlan_results

    def get_vlan_infos(self):
        self.__update_config()
        if self.dev_type == "s350":  # s350 device need special treatment since there is no native napalm integration for those products
            vlan_data = Vlan(self.dev_creds).get_vlan_data()
        else:
            self.__create_connection()
            vlans = self.conn.get_vlans()
            self.conn.close()
            vlan_data = SSH.reformat_vlan_data(vlans)  # reformats the data to an interface centric design
        self._logger.spam(vlan_data)
        return {"vlan": vlan_data}

    @staticmethod
    def config_template():
        settings = Settings(default_timeout=30*60)
        settings.add(SettingsItem(SettingsItemType.STRING, "SSH_USERNAME", "username", "NetWatch"))
        settings.add(SettingsItem(SettingsItemType.STRING, "SSH_PASSWORD", "password", "!NetWatch2021?"))
        settings.add(SettingsItem(SettingsItemType.STRING, "SSH_ENABLE_SECRET", "enable secret", "",
                                  settings_required=False))  # HTL-Villach
        # the enable secret is not needed at this time for anything - therefore it is optional
        settings.add(SettingsItem(SettingsItemType.ENUM, "SSH_DEVICE_TYPE", "device type", "s350", ["s350", "nxos"]))
        settings.add(SettingsItem(SettingsItemType.ENUM, "SSH_TRANSPORT_PROTOCOL", "transport protocol (only relevant for Nexus devices)", "http", ["http", "https"]))
        # the transport protocol is the protocol used for the nexus API requests - nexus does not use SSH
        return settings

    def worker(self):
        data = {}
        data.update(self.get_lldp_infos())
        data.update(self.get_vlan_infos())
        return ModuleData(data, [], {}, OutputType.DEFAULT)

