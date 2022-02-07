from src.module_data import ModuleData, OutputType, LiveData
from src.utilities import Utilities
import json


class DeviceData:
    def __init__(self):
        self.static_data = {}
        self.live_data = {}
        self.events = {}
        self.external_events = {}

    def add_module_data(self, module_data: ModuleData):
        self.static_data.update(module_data.static_data)
        if type(module_data) is ModuleData:
            self.add_live_data_list(module_data.live_data)  # TODO: REMOVE
            if module_data.output_type == OutputType.DEFAULT:
                self.events.update(module_data.events)
            elif module_data.output_type == OutputType.EXTERNAL_DATA_SOURCES:
                self.external_events.update(module_data.events)
        elif type(module_data) is DeviceData:
            self.live_data = Utilities.update_multidimensional_dict(self.live_data, module_data.live_data)
            self.events.update(module_data.events)
            self.external_events.update(module_data.external_events)

    def convert_to_key_value_list(self, input_dict: dict):
        key_val = []
        system_data = {}
        for key, val in input_dict.items():
            if type(val) == dict:
                first_run = True
                is_single_dict = False
                for current_key, current_value in val.items():
                    if first_run and type(current_value) != dict:
                        is_single_dict = True
                        break
                    key_val.append({
                        "key": key,
                        "identifier": current_key,
                        "value": current_value
                    })
                    first_run = False
                if is_single_dict:
                    key_val.append({"key": key, "identifier": None, "value": val})
            else:
                system_data[key] = val
        # single values
        if system_data:
            key_val.append({"key": "system", "identifier": None, "value": system_data})
        return key_val

    def add_live_data_list(self, input_list: list[LiveData]):
        for item in input_list:
            if type(item) == LiveData:
                if item.name not in self.live_data:
                    self.live_data[item.name] = {}
                print(item.timestamp)
                self.live_data[item.name].update({item.timestamp: item.value})
            else:
                print(type(item), item)
        print(self.live_data)

    def serialize(self):
        return {"static_data": self.convert_to_key_value_list(self.static_data),
                "live_data": self.live_data,
                "events": self.events,
                }

    def __str__(self):
        return json.dumps({"static_data": self.static_data,
                           "live_data": self.live_data,
                           "events": self.events})
