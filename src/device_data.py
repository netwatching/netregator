from src.module_data import ModuleData
import json


class DeviceData:
    def __init__(self):
        self.static_data = {}
        self.live_data = {}
        self.events = {}

    def add_module_data(self, module_data: ModuleData):
        self.static_data.update(module_data.static_data)
        self.live_data.update(module_data.live_data)
        self.events.update(module_data.events)

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

    def serialize(self):
        return {"static_data": self.convert_to_key_value_list(self.static_data),
                "live_data": self.convert_to_key_value_list(self.live_data),
                "events": self.events,
                }

    def __str__(self):
        return json.dumps({"static_data": self.static_data,
                           "live_data": self.live_data,
                           "events": self.events})
