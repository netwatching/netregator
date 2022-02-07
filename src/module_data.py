import time
import json
from enum import Enum
from typing import List


class OutputType(Enum):
    DEFAULT = 0
    EXTERNAL_DATA_SOURCES = 1


class LiveData:
    def __init__(self, name: str, value: float, timestamp: time = time.time()):
        self.name = name
        self.value = value
        self.timestamp = timestamp


class ModuleData:
    def __init__(self, static_data: dict, live_data: List[LiveData], events: dict,
                 output_type: OutputType = OutputType.DEFAULT):
        self.static_data = static_data
        self.live_data = live_data
        self.events = events
        self.timestamp = time.time()
        self.output_type = output_type

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
    def output_type(self):
        return self.__output_type

    @output_type.setter
    def output_type(self, output_type: OutputType):
        self.__output_type = output_type

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
                "timestamp": self.timestamp,
                "output_type": self.output_type})
