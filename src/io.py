import requests
import jwt
import datetime
import json
from decouple import config

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
        self._session = requests.session()
        self._demo = True
        self._id = None
        self._secret = "admin"
        self._token = None
        self._url = config("IP")
        self.__conter = 0
        self._session.auth = JWTAuth(self)
        self._session.headers['Content-Type'] = 'application/json'

    def login(self):
        # generate new token or use old one
        reauth = False
        jwt_options = {
            'verify_signature': False,
            'verify_exp': False,
            'verify_nbf': False,
            'verify_iat': True,
            'verify_aud': False
        }
        # first run of code
        if self._token is None:
            reauth = True
        # if not first Run
        if reauth is False:
            try:
                time = datetime.datetime.utcfromtimestamp(jwt.decode(self._token, algorithms=["HS512", "HS256"], options=jwt_options)["exp"])
                # check if code already expired
                if datetime.datetime.utcnow() > (time - datetime.timedelta(seconds=60)):
                    reauth = True
            except jwt.exceptions.DecodeError:
                reauth = True
        # generate new Code
        if reauth:
            payload = {
                "token": self._secret
            }
            req = self._session.post(f"{self._url}/api/aggregator-login", timeout=5, json=payload)
            if req.status_code == requests.codes.ok:
                output = req.json()
                self._id = output["aggregator_id"]
                self._token = output["token"]
                return self._token
        else:
            return self._token
    
    def send_data(self, data):
        req = self._session.post(f"{self._url}/api/devices/data", auth=JWTAuth(self), json=data)
        if req.status_code == requests.codes.ok:
            return True
        else:
            return False

    def get_running_threads(self):
        if not self._demo:
            try:
                req = self._session.get(f"{self._url}/api/aggregator/{self._id}", auth=JWTAuth(self), timeout=5)
                if req.status_code == requests.codes.ok:
                    output = req.json()
                    # print(output["devices"])
                    return output["devices"]
                else:
                    return []
            except Exception as ex:
                print(ex)
                return []
        else:
            data = []
            modules = []
            modules.append({"name": "snmb", "config": {}})
            data.append({"id": "1", "name": "Ubi", "timeout": 1, "type": "Ubiquiti", "ip": "172.31.37.95", "modules": modules})
            data.append({"id": "2", "name": "Zabbi", "timeout": 10, "type": "Ubiquiti", "ip": "zabbix.htl-vil.local", "modules": [{"name": "problems", "config": {}}]})
            data.append({"id": "3", "name": "Cisco", "timeout": 10, "type": "Cisco", "ip": "172.31.8.81", "modules": modules})

            #if(self.__conter % 5 == 0):
            #data.append({"id": "3", "name": "myThread3", "timeout": 10, "type": "Ubiquiti", "ip": "192.168.3.1", "modules": modules})
            self.__conter +=1
            print(data)
            return data
    
class JWTAuth(requests.auth.AuthBase):
    def __init__(self, api: API):
        self.token = api.login()
    def __call__(self, r):
        # print(self.token)
        r.headers["Authorization"] = "Bearer " + self.token
        return r