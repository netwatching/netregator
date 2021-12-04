from pysnmp.hlapi import *


class SNMP:
    def __init__(self, community_string, hostname, port=161):
        self.__community_string = community_string
        self.__hostname = hostname
        self.__port = port

    def get_single_value_by_oid(self, oid):
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.__community_string, mpModel=0),
            UdpTransportTarget((self.__hostname, self.__port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)), lookupMib=True, lexicographicMode=False
        )
        (error_indication, error_status, error_index, var_binds) = next(iterator)
        name, value = var_binds[0]  # name is ObjectName object - value is number object
        return value.prettyPrint()

    def __getvar_binds_by_name(self, name, mib_name):
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.__community_string, mpModel=0),
            UdpTransportTarget((self.__hostname, self.__port), timeout=1, retries=5),
            ContextData(),
            ObjectType(ObjectIdentity(mib_name, name, 0))
        )
        (error_indication, error_status, error_index, var_binds) = next(iterator)

        if error_indication:
            print(error_indication)
            raise Exception(error_indication)
        elif error_status:
            raise Exception('%s at %s' % (error_status.prettyPrint(), error_index and var_binds[int(error_index) - 1][0] or '?'))
        else:
            if var_binds:
                return var_binds
            else:
                raise Exception(f"no value returned for {name} in MIB: {mib_name}")

    def get_single_value_by_name(self, name, mib_name='SNMPv2-MIB'):
        name, value = self.__getvar_binds_by_name(name, mib_name)[0]  # name is ObjectName object - value is number object
        return value.prettyPrint()

    def get_single_value_by_name_with_name(self, name, mib_name='SNMPv2-MIB'):
        oid, value = self.__getvar_binds_by_name(name, mib_name)[0]  # name is ObjectName object - value is number object
        _, name, index = oid.getMibSymbol()  # _ is MIB name
        value = value.prettyPrint()
        return {name: value}

    def get_table(self, arguments_list: list, mib_name):
        all_entries = {}
        _var_binds = []

        for key in arguments_list:
            _var_binds.append(ObjectType(ObjectIdentity(mib_name, key)))

        iterator = nextCmd(
            SnmpEngine(),
            CommunityData(self.__community_string),
            UdpTransportTarget((self.__hostname, 161)),
            ContextData(),
            *_var_binds,
            lexicographicMode=False,
            lookupMib=True
        )

        for error_indication, error_status, error_index, var_binds in iterator:
            if error_indication:
                print(error_indication)
                break
            elif error_status:
                print('%s at %s' % (error_status.prettyPrint(), error_index and var_binds[int(error_index) - 1][0] or '?'))
                break
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
                        # interface_data.append((mib, name, index, value))
                        # if index in interface_data:
                        #interface_data[index].update({name: value})
                        # else:
                        #     interface_data[index] = {name: value}

                        # print(f"{mib=}")
                        # print(f"{name=}")
                        # print(f"{index=}")
                        # print(f"{value.prettyPrint()=}")
                        all_entries[index].update({name: value})
                else:
                    print("no value returned")
        return all_entries


class DataSources:
    def __init__(self, snmp: SNMP):
        self.__snmp = snmp

    def get_hostname(self):
        name = self.__snmp.get_single_value_by_name('sysName')
        return {"hostname": name}

    def get_object_id(self):  # milliseconds
        oid = self.__snmp.get_single_value_by_name('sysObjectID')
        return {"object_id": oid}

    def get_uptime(self):  # milliseconds
        uptime = int(self.__snmp.get_single_value_by_name('sysUpTime'))*10
        return {"uptime": uptime}

    def get_description(self):
        description = self.__snmp.get_single_value_by_name('sysDescr')
        return {"description": description}

    def get_contact(self):
        contact = self.__snmp.get_single_value_by_name('sysContact')
        return {"contact": contact}

    def get_name(self):
        name = self.__snmp.get_single_value_by_name('sysName')
        return {"name": name}

    def get_location(self):
        location = self.__snmp.get_single_value_by_name('sysLocation')
        return {"location": location}

    def get_ip_data(self):
        ip_data = {}
        keys = [
            "ipForwarding",
            "ipDefaultTTL",
            "ipInReceives",
            "ipInHdrErrors",
            "ipInAddrErrors",
            "ipForwDatagrams",
            "ipInUnknownProtos",
            "ipInDiscards",
            "ipInDelivers",
            "ipOutRequests",
            "ipOutDiscards",
            "ipOutNoRoutes",
            "ipReasmTimeout",
            "ipReasmReqds",
            "ipReasmOKs",
            "ipReasmFails",
            "ipFragOKs",
            "ipFragFails",
            "ipFragCreates",
            "ipRoutingDiscards",
        ]
        for key in keys:
            ip_data.update(self.__snmp.get_single_value_by_name_with_name(key, "IP-MIB"))
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

        return {"services": {"services": services}}

    def get_interfaces(self):  # 1.3.6.1.2.1.2.2.1
        _keys = ['ifIndex',
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
                 'ifOutErrors']

        return {"interfaces": self.__snmp.get_table(_keys, "IF-MIB")}

    def get_ip_addresses(self):
        _keys = ['ipAdEntAddr',
                 'ipAdEntIfIndex',
                 'ipAdEntNetMask',
                 'ipAdEntBcastAddr',
                 'ipAdEntReasmMaxSize']
        return {"ipAddresses": self.__snmp.get_table(_keys, "IP-MIB")}

    def get_ip_routes(self):
        _keys = ['ipRouteDest',
                 'ipRouteIfIndex',
                 'ipRouteMetric1',
                 'ipRouteMetric2',
                 'ipRouteMetric3']
        return {"ipRoutes": self.__snmp.get_table(_keys, "IP-MIB")}
