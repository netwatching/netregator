import time
import json


class ModuleData:
    def __init__(self, static_data: dict, live_data: dict, events: dict):
        self.static_data = static_data
        self.live_data = live_data
        self.events = events
        self.timestamp = time.time()

    @property
    def static_data(self):
        return self.__static_data

    @static_data.setter
    def static_data(self, static_data):
        self.__static_data = static_data

    @property
    def live_data(self):
        return self.__live_data

    @live_data.setter
    def live_data(self, live_data):
        self.__live_data = live_data

    @property
    def events(self):
        return self.__events

    @events.setter
    def events(self, events):
        self.__events = events

    @property
    def timestamp(self):
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, timestamp: float):
        self.__timestamp = timestamp

    def __str__(self):
        return json.dumps({"static_data":self.static_data,
                "live_data":self.live_data,
                "events":self.events,
                "timestamp": self.timestamp})
