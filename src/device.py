class Device:

    def __init__(self, id, name: str, ip: str, type: str, timeout: int):
        self.name = name
        self.id = id
        self.ip = ip
        self.type = type
        self.timeout = timeout

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ip):
        self.__ip = ip

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, type):
        self.__type = type

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout: int):
        self.__timeout = int(timeout)