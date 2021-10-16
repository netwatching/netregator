import requests

class Config:
    def __init__(self, path="../src/config/config.json"):
        self._path = path
        with open(self._path) as file:
            self._data = json.load(file)
            self._file = file

    def reload_file(self):
        with open(self._path) as file:
            self._data = json.load(file)
            self._file = file

    def read_config_file(self, key):
        self.reload_file()
        try:
            return self._data[key]
        except Exception:
            return None

    def set_config_file(self, key, value):
        self.reload_file()
        self._data[key] = value
        with open(self._path, "w") as write_file:
            json.dump(self._data, write_file, ensure_ascii=False, indent=4)
        self.reload_file()

    def get_whole_file(self):
        self.reload_file()
        return self._data

class API:
    def __init__(self):
        self.__conter = 0
        pass

    def get_running_threads(self):
        data = {}
        data["1"] = {"name": "myThread", "type": "Cisco", "ip": "192.168.0.1"}
        data["2"] = {"name": "myThread2", "type": "Ubiquiti", "ip": "192.168.1.1"}

        if(self.__conter % 5 == 0):
            data["3"] = {"name": "myThread3", "type": "Ubiquiti", "ip": "192.168.3.1"}
        self.__conter +=1
        return data