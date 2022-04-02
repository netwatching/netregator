import requests
import jwt
import datetime
import json
from decouple import config
import urllib3
import logging
import os
from src.utilities import Utilities


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
        self._logger = Utilities.setup_logger()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._session = requests.session()
        self._demo = config("DEMO", False, cast=bool)
        self._id = None
        self._secret = config("SECRET", "admin", cast=str)
        self._access_token = None
        self._refresh_token = None
        self._url = config("IP")
        self.__counter = 0
        self._session.verify = config("SSL_VERIFY", True, cast=bool)
        self._session.trust_env = config("SSL_VERIFY", True, cast=bool)
        self._session.auth = JWTAuth(self)
        self._session.headers['Content-Type'] = 'application/json'

    def login(self):
        # generate new token or use old one
        redo_auth = False
        jwt_options = {
            'verify_signature': False,
            'verify_exp': False,
            'verify_nbf': False,
            'verify_iat': True,
            'verify_aud': False
        }
        # first run of code
        if self._access_token is None:
            redo_auth = True
        # if not first Run
        if redo_auth is False:
            try:
                time = datetime.datetime.utcfromtimestamp(
                    jwt.decode(self._access_token, algorithms=["HS512", "HS256"], options=jwt_options)["exp"])
                # check if code already expired
                if datetime.datetime.utcnow() > (time - datetime.timedelta(seconds=60)):
                    redo_auth = True
            except jwt.exceptions.DecodeError:
                redo_auth = True
        # generate new Code
        if redo_auth:
            use_refresh = True
            if self._refresh_token is not None:
                time = datetime.datetime.utcfromtimestamp(
                    jwt.decode(self._access_token, algorithms=["HS512", "HS256"], options=jwt_options)["exp"])
                if datetime.datetime.utcnow() > (time - datetime.timedelta(seconds=60)):
                    use_refresh = False
            else:
                use_refresh = False
            if use_refresh:
                req = self._session.post(f"{self._url}/api/aggregator-refresh",
                                         auth=JWTAuthRefreshToken(self._refresh_token))
                if req.status_code == requests.codes.ok:
                    output = req.json()
                    self._logger.debug(output)
                    self._access_token = output["access_token"]
                    self._refresh_token = output["refresh_token"]
                    return self._access_token
            else:
                payload = {
                    "token": self._secret
                }
                req = self._session.post(f"{self._url}/api/aggregator-login", json=payload)
                if req.status_code == requests.codes.ok:
                    output = req.json()
                    self._logger.debug(output)
                    self._id = output["aggregator_id"]
                    self._access_token = output["access_token"]
                    self._refresh_token = output["refresh_token"]
                    return self._access_token
                elif req.status_code == requests.codes.unauthorized:
                    self._logger.critical("Invalid client secret!")
                    os._exit(22)
        else:
            return self._access_token

    def send_data(self, data):
        req = self._session.post(f"{self._url}/api/devices/data", auth=JWTAuth(self), json=data)
        # self._logger.error(req.request.body)
        if req.status_code == requests.codes.ok:
            self._logger.info("Data sent successfully.")
            return True
        else:
            self._logger.error(f"Status code: {req.status_code}, response: {req.text}")
            return False

    def get_running_threads(self):
        if not self._demo:
            try:
                req = self._session.get(f"{self._url}/api/aggregator/{self._id}", auth=JWTAuth(self))
                if req.status_code == requests.codes.ok:
                    output = req.json()
                    self._logger.debug(output)
                    return output
                else:
                    self._logger.debug(req.json())
                    return []
            except Exception as ex:
                self._logger.critical(f"get_running_threads: {ex}")
                return []
        else:
            data = []
            modules = [{"name": "unifi_lldp", "config": {}}]
            # data.append(
            #    {"id": "1", "name": "Ubi", "timeout": 1, "type": "Ubiquiti", "ip": "172.31.37.95", "modules": modules})
            data.append({"id": "2", "name": "Zabbi", "timeout": 10, "type": "Ubiquiti", "ip": "172.31.37.77",
                         "modules": modules})
            data.append({"id": "798787", "name": "Zabbix", "timeout": 10, "type": "Zabbix", "ip": "zabbix.htl-vil.local",
                         "modules": [{"name": "events", "config": {}}]})

            # if(self.__conter % 5 == 0):
            #     data.append({"id": "3", "name": "Cisco", "timeout": 10, "type": "Cisco", "ip": "172.31.8.81",
            #                  "modules": modules})
            # else:
            # data.append({"id": "3", "name": "Cisco", "timeout": 10, "type": "Cisco", "ip": "172.31.8.81",
            # "modules": modules})
            self.__counter += 1
            # print(data)
            return data

    def send_version_string(self, version):
        if version == "%VER%":
            version = "v0.0-DEV"
        req = self._session.post(f"{self._url}/api/aggregator/{self._id}/version", json={"version": version}, auth=JWTAuth(self))
        if req.status_code == requests.codes.ok:
            return True
        else:
            self._logger.critical(f"send_version_string: {req.text}")
            return False

    def send_known_modules(self, modules):
        req = self._session.post(f"{self._url}/api/aggregator/{self._id}/modules", json={"modules": modules},
                                 auth=JWTAuth(self))
        if req.status_code == requests.codes.ok:
            self._logger.info(f"send_known_modules: {req.text}")
            return True
        else:
            self._logger.critical(f"send_known_modules: {req.text}")
            return False


class JWTAuth(requests.auth.AuthBase):
    def __init__(self, api: API):
        self.token = api.login()

    def __call__(self, r):
        # print(self.token)
        r.headers["Authorization"] = "Bearer " + self.token
        #print(self.token)
        return r

class JWTAuthRefreshToken(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        # print(self.token)
        r.headers["Authorization"] = "Bearer " + self.token
        #print(self.token)
        return r
