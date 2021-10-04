
class Worker:
    def __init__(self, id, name, ip, type):
        self.name = name
        self.id = id
        self.ip = ip
        self._thread = None
        self.type = type

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

    def start_thread(self):
        return True


if __name__ == '__main__':
    worker = Worker(1,"abc", "10.10.10.10", "cisco")
    worker.id = 20
    print(worker.id)
