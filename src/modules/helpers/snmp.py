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

    def get_single_value_by_name(self, name, mib_name='SNMPv2-MIB'):
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.__community_string, mpModel=0),
            UdpTransportTarget((self.__hostname, self.__port), timeout=1, retries=5),
            ContextData(),
            ObjectType(ObjectIdentity(mib_name, name, 0))
        )
        (error_indication, error_status, error_index, var_binds) = next(iterator)
        name, value = var_binds[0]  # name is ObjectName object - value is number object
        return value.prettyPrint()


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
        # get if number
        # number = int(snmp.get_single_value_by_oid('1.3.6.1.2.1.2.1.0'))
        # get ifnumber times descr
        # get ifnumber times type
        # get ifnumber times mtu
        # get ifnumber times speed
        # get ifnumber times phys addr
        # get ifnumber times admin status
        # get ifnumber times oper status
        # get ifnumber times last change
        # get ifnumber times InOctets
        # get ifnumber times Ucast pkts

        return {"interfaces": []}
