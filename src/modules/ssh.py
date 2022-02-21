from src.modules.module import Module
from decouple import config
from src.module_data import ModuleData, OutputType, Event, EventSeverity
import sys
import time
import napalm
import os
import json


class SSH(Module):
    def __init__(self, ip: str = None, timeout: int = None, *args, **kwargs):
        super().__init__(ip, timeout, *args, **kwargs)
        # devicetype & creds -> settingsAPI
        self.dev_type = 's350'
        self.dev_creds = {
            'hostname': '172.31.8.81',
            'username': 'NetWatch',
            'password': '!NetWatch2021?',
            'optional_args': {'secret': 'HTL-Villach'}
        }
        self.__create_connection()

    def __create_connection(self):
        driver = napalm.get_network_driver(self.dev_type)
        self.conn = driver(**self.dev_creds)
        self.conn.open()

    def get_lldp_infos(self):
        output = self.conn.get_lldp_neighbors_detail()
        neighbors = {}

        for portname, data in output.items():
            neighbor = {
                portname:
                    {
                        "local_port": portname,
                        "remote_host": output[portname][0]["remote_system_name"],
                        "remote_chassis_id": output[portname][0]["remote_chassis_id"],
                        "remote_port": output[portname][0]["remote_port"],
                        "remote_system_description": output[portname][0]["remote_system_description"],
                        "remote_system_capability": output[portname][0]["remote_system_capab"][-1]
                    }
            }
            neighbors.update(neighbor)

        return {"neighbors": neighbors}

    def worker(self):
        #return ModuleData({}, [], [Event("successfully sent", EventSeverity.DEBUG)], OutputType.DEFAULT)
        return ModuleData(self.get_lldp_infos(), [], {}, OutputType.DEFAULT)
