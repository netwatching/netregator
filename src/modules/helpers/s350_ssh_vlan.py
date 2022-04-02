from __future__ import print_function
from __future__ import unicode_literals

from abc import ABC

import napalm_s350

from src.utilities import Utilities
import napalm
import re
from napalm.base.helpers import canonical_interface_name
import napalm.base.canonical_map


class Vlan:
    def __init__(self, dev_creds):
        self._logger = Utilities.setup_logger()
        self.dev_creds = dev_creds

    def get_vlan_data(self):
        conn = VlanS350(**self.dev_creds)
        conn.open()
        vlan_data = conn.get_vlan_data(expand_ports=True)
        r = Vlan.reformat_vlan_data_to_port_centric_format(vlan_data)
        conn.close()
        return r

    @staticmethod
    def reformat_vlan_data_to_port_centric_format(vlan_data):

        vlans = []
        for vlan in vlan_data:
            for tagged_port in vlan["tagged_ports"]:

                port_names = [port["port"] for port in vlans]
                if tagged_port in port_names:
                    port_index = port_names.index(tagged_port)
                    vlans[port_index]["vlans"].append({"id": vlan["id"], "name": vlan["name"]})
                else:
                    vlans.append({
                        "port": tagged_port,
                        "vlans": [{"id": vlan["id"], "name": vlan["name"]}],
                        "is_trunk": True
                    })
            for untagged_port in vlan["untagged_ports"]:
                port_names = [port["port"] for port in vlans]
                if untagged_port in port_names:
                    port_index = port_names.index(untagged_port)
                    vlans[port_index]["vlans"].append({"id": vlan["id"], "name": vlan["name"]})
                else:
                    vlans.append({
                        "port": untagged_port,
                        "vlans": [{"id": vlan["id"], "name": vlan["name"]}],
                        "is_trunk": False
                    })
        return vlans


class VlanS350(napalm_s350.S350Driver, ABC):  # napalm.base.NetworkDriver
    s350_base_interfaces = {
        **napalm.base.canonical_map.base_interfaces,
        "fa": "FastEthernet",
        "gi": "GigabitEthernet",
        "te": "TengigabitEthernet",
        "Po": "Link Aggregate ",
    }

    # [4, 22, 41, 60, 77, 78]
    # 1030      Printer             Po1         gi1/0/14-16,              S
    @staticmethod
    def _get_vlan_line_to_fields(line, fields_end):
        """ dynamic fields lenghts """
        line_elems = {}
        index = 0
        f_start = 0
        for f_end in fields_end:
            line_elems[index] = line[f_start:f_end].strip()
            index += 1
            f_start = f_end
        return line_elems

    @staticmethod
    def _get_vlan_fields_end(dashline):
        """ fields length are different device to device, detect them on horizontal lin """

        fields_end = [m.start() for m in re.finditer(" ", dashline)]
        fields_end.append(len(dashline))  # TODO: check if necessary

        return fields_end

    @staticmethod
    def _expand_ports(port):
        expanded_ports = []
        if re.match(r"^.+(\d)+-(\d)+$", port):
            from_to = re.search(r"(\d)+-(\d)+$", port).group()
            from_to = from_to.split("-")
            prefix = re.split(r"(\d)+-(\d)+$", port)[0]
            for i in range(int(from_to[0]), int(from_to[1]) + 1):
                expanded_ports.append(prefix + str(i))
            long_format_ports = []
            for e_port in expanded_ports:
                long_format_ports.append(canonical_interface_name(e_port, VlanS350.s350_base_interfaces))
            return long_format_ports
        return [canonical_interface_name(port, VlanS350.s350_base_interfaces)]

    def get_vlan_data(self, expand_ports=True):
        """get_vlan_data implementation for s350"""
        vlans = []

        output = self._send_command("show vlan")

        header = True  # cycle trough header
        vlan_id = 0
        currend_vlan_index = 0
        for line in output.splitlines():
            if header:
                # last line of header
                match = re.match(r"^---- -+ .*$", line)
                if match:
                    header = False
                    fields_end = VlanS350._get_vlan_fields_end(line)  # [4, 22, 41, 60, 77, 78]
                    print(f"{fields_end=}")
                continue

            line_elems = VlanS350._get_vlan_line_to_fields(line, fields_end)  # {0: '1312', 1: 'Students-3Jg', 2: 'gi1/0/1-12,', 3: '', 4: 'S', 5: ''}
            print(f"{line_elems=}")

            if line_elems[0] and line_elems[1] and line_elems[4]:
                vlan_id = line_elems[0]
                vlan_name = line_elems[1]
                vlans.append({
                    "id": int(vlan_id),
                    "name": vlan_name,
                    "tagged_ports": [],
                    "untagged_ports": [],
                    "created_by": list(line_elems[4])
                })
                currend_vlan_index = len(vlans)-1

            if line_elems[2]:
                ports = filter(None, line_elems[2].split(","))
                if expand_ports:
                    for port in ports:
                        vlans[currend_vlan_index]["tagged_ports"].extend(VlanS350._expand_ports(port))
                else:
                    vlans[currend_vlan_index]["tagged_ports"].extend(ports)
            if line_elems[3]:
                ports = filter(None, line_elems[3].split(","))
                if expand_ports:
                    for port in ports:
                        vlans[currend_vlan_index]["untagged_ports"].extend(VlanS350._expand_ports(port))
                else:
                    vlans[currend_vlan_index]["untagged_ports"].extend(ports)
        return vlans
