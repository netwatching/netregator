from pysnmp.hlapi import *
import re

from pysnmp.smi import view, builder

from src.utilities import Utilities


class SNMP:
    def __init__(self, community_string, hostname, port=161):
        self._logger = Utilities.setup_logger()
        self.__community_string = community_string
        self.__hostname = hostname
        self.__port = port

    def get_single_value_by_oid(self, oid):
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.__community_string, mpModel=0),
            UdpTransportTarget((self.__hostname, self.__port), timeout=1, retries=5),
            ContextData(),
            ObjectType(ObjectIdentity(oid)), lookupMib=True, lexicographicMode=False
        )
        (error_indication, error_status, error_index, var_binds) = next(iterator)
        name, value = var_binds[0]  # name is ObjectName object - value is number object
        return value.prettyPrint()

    def __get_var_binds_by_name(self, name, mib_name):
        self._logger.info(f"name: {name} mib-name: {mib_name}")
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.__community_string, mpModel=0),
            UdpTransportTarget((self.__hostname, self.__port), timeout=1, retries=5),  # TODO: add timout and retry everywhere
            ContextData(),
            ObjectType(ObjectIdentity(mib_name, name, 0))
        )
        (error_indication, error_status, error_index, var_binds) = next(iterator)

        if error_indication:
            # self._logger.error(error_indication)
            raise Exception(error_indication)
        elif error_status:
            # self._logger.error('%s at %s' % (error_status.prettyPrint(),
            #                                  error_index and var_binds[int(error_index) - 1][0] or '?'))
            raise Exception('%s at %s' % (error_status.prettyPrint(),
                                          error_index and var_binds[int(error_index) - 1][0] or '?'))
        else:
            if var_binds:
                return var_binds
            else:
                raise Exception(f"no value returned for {name} in MIB: {mib_name}")

    def get_single_value_by_name(self, name, mib_name='SNMPv2-MIB'):
        name, value = self.__get_var_binds_by_name(name, mib_name)[0]  # name is ObjectName object - value is number object
        return value.prettyPrint()

    def get_single_value_by_name_with_name(self, name, mib_name='SNMPv2-MIB'):
        oid, value = self.__get_var_binds_by_name(name, mib_name)[0]  # name is ObjectName object - value is number object
        #_, name, index = oid.getMibSymbol()  # _ is MIB name
        value = value.prettyPrint()
        #return {name: value}
        return value

    def get_table(self, arguments_list: list, mib_name):
        all_entries = {}
        _var_binds = []

        # for key in arguments_list:
        #     _var_binds.append(ObjectType(ObjectIdentity(mib_name, key)))

        # iterator = nextCmd(
        #     SnmpEngine(),
        #     CommunityData(self.__community_string),
        #     UdpTransportTarget((self.__hostname, 161), timeout=1, retries=5),
        #     ContextData(),
        #     *_var_binds,
        #     lexicographicMode=False,
        #     lookupMib=True
        # )

        for key in arguments_list:
            _var_binds.append(ObjectType(ObjectIdentity(mib_name, key)).resolveWithMib(view.MibViewController(builder.MibBuilder())))

        iterator = nextCmd(
            SnmpEngine(),
            CommunityData(self.__community_string),
            UdpTransportTarget((self.__hostname, 161), timeout=1, retries=5),
            ContextData(),
            *_var_binds,
            lexicographicMode=False
        )

        for error_indication, error_status, error_index, var_binds in iterator:
            if error_indication:
                # self._logger.error(error_indication)
                raise Exception(error_indication)
                # TODO: previously break - how can no variables found appear on no exception???
            elif error_status:
                # self._logger.error('%s at %s' % (error_status.prettyPrint(),
                #                                  error_index and var_binds[int(error_index) - 1][0] or '?'))
                raise Exception('%s at %s' % (error_status.prettyPrint(),
                                              error_index and var_binds[int(error_index) - 1][0] or '?'))
                # TODO: here too - break
            else:
                if var_binds:
                    #interface_data = {}
                    oid, _ = var_binds[0]
                    _, _, index = oid.getMibSymbol()
                    index = index[0].prettyPrint()
                    #interface_data[index] = {}
                    all_entries[index] = {}
                    for var_bind in var_binds:
                        oid, value = var_bind
                        mib, name, index = oid.getMibSymbol()
                        value = value.prettyPrint()
                        index = index[0].prettyPrint()
                        if value == 'No more variables left in this MIB View':
                            self._logger.info(f"found no variables left string in: {oid=}, {value=}, {mib=}, {name=}, "
                                               f"{index=}, {var_binds=}")
                        # interface_data.append((mib, name, index, value))
                        # if index in interface_data:
                        #interface_data[index].update({name: value})
                        # else:
                        #     interface_data[index] = {name: value}

                        print(f"{mib=}")
                        print(f"{name=}")
                        print(f"{index=}")
                        print(f"{value=}")
                        print(f"{index.prettyPrint()=}")
                        print(f"{value.prettyPrint()=}")

                        # print(f"{value.prettyPrint()=}")
                        all_entries[index].update({name: value})
                else:
                    self._logger.warning("no value returned")
        return all_entries


class DataSources:
    def __init__(self, snmp: SNMP):
        self.__snmp = snmp
        self._logger = Utilities.setup_logger()

    # def get_hostname(self):
    #     name = self.__snmp.get_single_value_by_name('sysName')
    #     return {"hostname": name}
    #
    # def get_object_id(self):  # milliseconds
    #     oid = self.__snmp.get_single_value_by_name('sysObjectID')
    #     return {"object_id": oid}
    #
    # def get_uptime(self):  # milliseconds
    #     uptime = int(self.__snmp.get_single_value_by_name('sysUpTime'))*10
    #     return {"uptime": uptime}
    #
    # def get_description(self):
    #     description = self.__snmp.get_single_value_by_name('sysDescr')
    #     return {"description": description}
    #
    # def get_contact(self):
    #     contact = self.__snmp.get_single_value_by_name('sysContact')
    #     return {"contact": contact}
    #
    # def get_name(self):
    #     name = self.__snmp.get_single_value_by_name('sysName')
    #     return {"name": name}
    #
    # def get_location(self):
    #     location = self.__snmp.get_single_value_by_name('sysLocation')
    #     return {"location": location}

    def get_system_data(self):
        system_data = {}
        # keys = [
        #     "sysName",
        #     "sysObjectID",
        #     "sysUpTime",
        #     "sysDescr",
        #     "sysContact",
        #     "sysLocation"
        # ]

        system_data["name"] = self.__snmp.get_single_value_by_name_with_name("sysName")
        system_data["uptime"] = int(self.__snmp.get_single_value_by_name_with_name("sysUpTime")) * 10
        system_data["description"] = self.__snmp.get_single_value_by_name_with_name("sysDescr")
        system_data["contact"] = self.__snmp.get_single_value_by_name_with_name("sysContact")
        system_data["location"] = self.__snmp.get_single_value_by_name_with_name("sysLocation")

        # for key in keys:
        #     system_data.update(self.__snmp.get_single_value_by_name_with_name(key))
        return {"system": system_data}

    def get_ip_data(self):
        ip_data = {}
        # keys = [
        #     "ipForwarding",
        #     "ipDefaultTTL",
        #     "ipInReceives",
        #     "ipInHdrErrors",
        #     "ipInAddrErrors",
        #     "ipForwDatagrams",
        #     "ipInUnknownProtos",
        #     "ipInDiscards",
        #     "ipInDelivers",
        #     "ipOutRequests",
        #     "ipOutDiscards",
        #     "ipOutNoRoutes",
        #     "ipReasmTimeout",
        #     "ipReasmReqds",
        #     "ipReasmOKs",
        #     "ipReasmFails",
        #     "ipFragOKs",
        #     "ipFragFails",
        #     "ipFragCreates",
        #     "ipRoutingDiscards"
        # ]

        ip_data["forwarding"] = self.__snmp.get_single_value_by_name_with_name("ipForwarding")  # TODO: check for value (int / bool can forward / is router or only host)
        ip_data["default_ttl"] = self.__snmp.get_single_value_by_name_with_name("ipDefaultTTL")
        ip_data["in_receives"] = self.__snmp.get_single_value_by_name_with_name("ipInReceives")
        ip_data["in_hdr_errors"] = self.__snmp.get_single_value_by_name_with_name("ipInHdrErrors")
        ip_data["in_addr_errors"] = self.__snmp.get_single_value_by_name_with_name("ipInAddrErrors")
        ip_data["forward_datagrams"] = self.__snmp.get_single_value_by_name_with_name("ipForwDatagrams")
        ip_data["in_unknown_protocol"] = self.__snmp.get_single_value_by_name_with_name("ipInUnknownProtos")
        ip_data["in_discards"] = self.__snmp.get_single_value_by_name_with_name("ipInDiscards")
        ip_data["in_delivers"] = self.__snmp.get_single_value_by_name_with_name("ipInDelivers")
        ip_data["out_requests"] = self.__snmp.get_single_value_by_name_with_name("ipOutRequests")
        ip_data["out_discards"] = self.__snmp.get_single_value_by_name_with_name("ipOutDiscards")
        ip_data["out_no_routes"] = self.__snmp.get_single_value_by_name_with_name("ipOutNoRoutes")
        ip_data["reasm_timeout"] = self.__snmp.get_single_value_by_name_with_name("ipReasmTimeout")
        # ip_data["reasm_ok"] = self.__snmp.get_single_value_by_name_with_name("ipReasmOKs")  # deprecated
        # ip_data["reasm_fails"] = self.__snmp.get_single_value_by_name_with_name("ipReasmFails")  # deprecated
        # ip_data["fragments_ok"] = self.__snmp.get_single_value_by_name_with_name("ipFragOKs")  # deprecated
        # ip_data["fragments_fails"] = self.__snmp.get_single_value_by_name_with_name("ipFragFails")  # deprecated
        # ip_data["fragments_creates"] = self.__snmp.get_single_value_by_name_with_name("ipFragCreates")  # deprecated
        ip_data["routing_discards"] = self.__snmp.get_single_value_by_name_with_name("ipRoutingDiscards")


        # for key in keys:
        #     ip_data.update(self.__snmp.get_single_value_by_name_with_name(key, "IP-MIB"))
        return {"ip": ip_data}

    def get_services(self):
        services_key = int(self.__snmp.get_single_value_by_name('sysServices'))  # https://oidref.com/1.3.6.1.2.1.1.7
        services = {}  # services by OSI layers

        services["ApplicationLayer"] = services_key >= 64
        if services_key >= 64:
            services_key -= 64
        services["PresentationLayer"] = services_key >= 32
        if services_key >= 32:
            services_key -= 32
        services["SessionLayer"] = services_key >= 16
        if services_key >= 16:
            services_key -= 16
        services["TransportLayer"] = services_key >= 8
        if services_key >= 8:
            services_key -= 8
        services["NetworkLayer"] = services_key >= 4
        if services_key >= 4:
            services_key -= 4
        services["DataLinkLayer"] = services_key >= 2
        if services_key >= 2:
            services_key -= 2
        services["PhysicalLayer"] = services_key >= 1
        if services_key >= 1:
            services_key -= 1

        return {"services": services}

    def get_interfaces(self):  # 1.3.6.1.2.1.2.2.1
        _keys = [
            'ifIndex',
            'ifDescr',
            'ifType',
            'ifMtu',
            'ifSpeed',
            'ifPhysAddress',
            'ifAdminStatus',
            'ifOperStatus',
            'ifLastChange',
            'ifInOctets',
            'ifInUcastPkts',
            'ifInNUcastPkts',
            'ifInDiscards',
            'ifInErrors',
            'ifInUnknownProtos',
            'ifOutOctets',
            'ifOutUcastPkts',
            'ifOutNUcastPkts',
            'ifOutDiscards',
            'ifOutErrors'
        ]

        old_name_values = self.__snmp.get_table(_keys, "IF-MIB")
        new_values = {}
        for _, val in old_name_values.items():
            infos = {}
            # ^[a-zA-Z]*[0-9]*(/[0-9]*)*
            if re.match(r"^[a-zA-Z]+[0-9]+(/[0-9]+){1,2}$", val["ifDescr"]):
                # cisco description e.g. TenGigabitEthernet3/23/4
                nums = re.split(r"^[a-zA-Z]*", val["ifDescr"])[1]
                iface_infos = nums.split("/")
                if len(iface_infos) == 3:
                    infos["blade"] = iface_infos[0]
                    infos["slot"] = iface_infos[1]
                    infos["port"] = iface_infos[2]
                elif len(iface_infos) == 2:
                    infos["slot"] = iface_infos[0]
                    infos["port"] = iface_infos[1]
                infos["definition"] = re.split(r"[0-9]", val["ifDescr"])[0]
                key = val["ifDescr"]
            elif re.match(r"^Slot: [0-9]+ Port: [0-9]+ \w+", val["ifDescr"]):
                # unifi sw desrc e.g. Slot: 0 Port: 51 10G - Level  /  Slot: 0 Port: 7 Gigabit - Level
                iface_infos = val["ifDescr"].split(" ")
                infos["slot"] = iface_infos[1]  # 2
                infos["port"] = iface_infos[3]  # 12
                infos["definition"] = iface_infos[4]  # 10G
                key = f"Port {infos['port']}"
            else:
                key = val["ifDescr"]
                self._logger.spam(f"ifDescr {val['ifDescr']} did not match any regex")

            if val["ifType"] in ["ethernetCsmacd", "ieee8023adLag", "softwareLoopback"]:
                new_values[key] = {
                    "key": key,
                    "index": int(val["ifIndex"]),
                    "description": val["ifDescr"],
                    "type": val["ifType"],
                    "mtu": int(val["ifMtu"]),
                    "speed": int(val["ifSpeed"]),  # e.g. 4294967295
                    "mac_address": val["ifPhysAddress"],  # e.g. "up"
                    "admin_status": val["ifAdminStatus"],
                    "operating_status": val["ifOperStatus"],
                    "last_change": int(val["ifLastChange"]) * 10,
                    # sysuptime timestamp at which operational state changed
                    "in_bytes": int(val["ifInOctets"]),
                    "in_unicast_packets": int(val["ifInUcastPkts"]),
                    "in_non_unicast_packets": int(val["ifInNUcastPkts"]),
                    "in_discards": int(val["ifInDiscards"]),
                    "in_errors": int(val["ifInErrors"]),
                    "in_unknown_protocolls": int(val["ifInUnknownProtos"]),
                    "out_bytes": int(val["ifOutOctets"]),
                    "out_unicast_packets": int(val["ifOutUcastPkts"]),
                    "out_non-unicast_packets": int(val["ifOutNUcastPkts"]),
                    "out_discards": int(val["ifOutDiscards"]),
                    "out_errors": int(val["ifOutErrors"])
                }

            elif not val["ifType"] in ["other"]:
                self._logger.warning(f"unknown interface type: {val['ifType']}, description: {val['ifDescr']}")

            if infos:
                new_values[key].update(infos)

            """
            ethernetCsmacd (Slot: 0 Port: 22 Gigabit - Level)
            other ( CPU Interface for Slot: 5 Port: 1)
            ieee8023adLag ( Link Aggregate 1)
            """

        return {"network_interfaces": new_values}

    def get_ip_addresses(self):
        _keys = [
            'ipAdEntAddr',
            'ipAdEntIfIndex',
            'ipAdEntNetMask',
            'ipAdEntBcastAddr',
            # 'ipAdEntReasmMaxSize'
        ]

        old_name_values = self.__snmp.get_table(_keys, "IP-MIB")
        new_values = {}
        for key, val in old_name_values.items():
            if not val["ipAdEntAddr"] == "127.0.0.1":
                new_values[key] = {
                    "address": val["ipAdEntAddr"],
                    "interface_index": int(val["ipAdEntIfIndex"]),
                    "netmask": val["ipAdEntNetMask"],
                    "broadcast_address": val["ipAdEntBcastAddr"],
                }

        return {"ipAddresses": new_values}
