from src.module_data import ModuleData, OutputType, LiveData, Event
from src.utilities import Utilities
import json
import time
import typing


class DeviceData:
    def __init__(self):
        self._logger = Utilities.setup_logger()
        self.static_data = {}
        self.live_data = {}
        self.events = []
        self.external_events = {}

    def add_module_data(self, module_data: ModuleData):
        self.static_data.update(module_data.static_data)
        if type(module_data) is ModuleData:
            #self.add_live_data_or_event_list(module_data.live_data)
            Utilities.update_multidimensional_dict(self.live_data,
                                                   DeviceData.livedata_multidimensional_parser(module_data.live_data))
            if module_data.output_type == OutputType.DEFAULT:
                self.events.extend(module_data.events)
            elif module_data.output_type == OutputType.EXTERNAL_DATA_SOURCES:
                self.external_events.update(module_data.events)
        elif type(module_data) is DeviceData:
            self.live_data = Utilities.update_multidimensional_dict(self.live_data, module_data.live_data)
            self.events.extend(module_data.events)
            self.external_events.update(module_data.external_events)

    @staticmethod
    def livedata_multidimensional_parser(live_data_list: list[LiveData]):
        output = {}
        for live_data in live_data_list:
            current_layer = {}
            c_output_layer = current_layer
            for c_mapping in live_data.mapping:
                c_output_layer[c_mapping] = {}
                c_output_layer = c_output_layer[c_mapping]
            c_output_layer[live_data.name] = {live_data.timestamp: live_data.value}
            Utilities.update_multidimensional_dict(output, current_layer)
        return output

    @staticmethod
    def convert_to_key_value_list(input_dict: dict):
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

    def add_live_data_or_event_list(self, input_list: typing.Union[list[LiveData], list[Event]]):
        for item in input_list:
            if type(item) == LiveData:
                if item.name not in self.live_data:
                    self.live_data[item.name] = {}
                self.live_data[item.name].update({item.timestamp: item.value})
            elif type(item) == Event:
                self.events.append(item)
            else:
                self._logger.error("Tried to add invalid Data Type. Data can either be ListData or Event.")

    def serialize(self):
        return {  # "static_data": self.convert_to_key_value_list(self.static_data),
            "static_data": self.static_data,
            "live_data": self.live_data,
            "events": [item.serialize() for item in self.events],
        }

    def __str__(self):
        return json.dumps({"static_data": self.static_data,
                           "live_data": self.live_data,
                           "events": self.events})

if __name__ == "__main__":
    livedata_list = []
    livedata_list.append(LiveData(name="cpu", value=70, mapping=("my_data",)))
    time.sleep(5)
    livedata_list.append(LiveData(name="cpu", value=71, mapping=("my_data",)))
    print(DeviceData.livedata_multidimensional_parser(livedata_list))
