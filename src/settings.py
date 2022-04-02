import json
from enum import Enum


class SettingsItemType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ENUM = "enum"


# noinspection PyTypeChecker
class SettingsItem:
    def __init__(self, settings_type: SettingsItemType, settings_id: str, settings_title: str,
                 settings_default_value, settings_enum_items: list = None, settings_required: bool = True):
        self.settings_type = settings_type
        self.settings_id = settings_id
        self.settings_title = settings_title
        self.settings_enum_items = settings_enum_items
        self.settings_default_value = settings_default_value
        self.settings_required = settings_required

    def serialize(self):
        return_schema = {}
        additional = {}
        output_settings_type = self.settings_type
        if self.settings_type == SettingsItemType.ENUM:
            additional["enum"] = self.settings_enum_items
            output_settings_type = SettingsItemType.STRING
        return_schema[self.settings_id] = {"type": output_settings_type.value, "title": self.settings_title}
        return_schema[self.settings_id].update(additional)
        return return_schema


# noinspection PyTypeChecker
class Settings:
    def __init__(self, seed_default_values: bool = True, default_timeout: int = 5):
        self._settings_items = dict()
        self.default_timeout = default_timeout
        if seed_default_values:
            self.seed_default_values()

    def add(self, item: SettingsItem):
        self._settings_items[item.settings_id] = item

    def serialize(self):
        serialized_settings_items = dict()
        serialized_default_values = dict()
        required_settings = []
        for k in self._settings_items:
            serialized_settings_items.update(self._settings_items[k].serialize())
            if self._settings_items[k].settings_default_value:
                serialized_default_values[self._settings_items[k].settings_id] = self._settings_items[k].settings_default_value
            # required settings
            if self._settings_items[k].settings_required:
                required_settings.append(self._settings_items[k].settings_id)

        return {
            "type": "object",
            "properties": serialized_settings_items,
            "required": required_settings
        }, serialized_default_values

    def seed_default_values(self):
        self.add(SettingsItem(settings_type=SettingsItemType.NUMBER, settings_id="timeout", settings_title="Timeout",
                              settings_default_value=self.default_timeout))


if __name__ == "__main__":
    settings = Settings()
    settings.add(SettingsItem(settings_type=SettingsItemType.STRING, settings_id="community_string",
                              settings_title="Community String", settings_default_value="test"))
    settings.add(SettingsItem(settings_type=SettingsItemType.NUMBER, settings_id="community_number",
                              settings_title="Community Number", settings_default_value=1))
    settings.add(SettingsItem(settings_type=SettingsItemType.ENUM, settings_id="community_enum",
                              settings_title="Community Enum", settings_default_value="test1",
                              settings_enum_items=["test1", "test2"], settings_required=False))
    settings.add(SettingsItem(SettingsItemType.ENUM, "SSH_DEVICE_TYPE", "device type", "s350", ["s350", "nxos"]))
    test_schema, test_data = settings.serialize()
    print(test_schema)
    print(test_data)
