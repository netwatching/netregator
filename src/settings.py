from enum import Enum
import json


class SettingsItemType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ENUM = "enum"


# noinspection PyTypeChecker
class SettingsItem:
    def __init__(self, settings_type: SettingsItemType, settings_id: str, settings_title: str, settings_enum_items: list = None):
        self.settings_type = settings_type
        self.settings_id = settings_id
        self.settings_title = settings_title
        self.settings_enum_items = settings_enum_items

    def serialize(self):
        return_data = {}
        additional = {}
        if self.settings_type == SettingsItemType.ENUM:
            additional["enum"] = self.settings_enum_items
            self.settings_type = SettingsItemType.STRING
        return_data[self.settings_id] = {"type": self.settings_type.value, "title": self.settings_title}
        return_data.update(additional)
        return return_data


# noinspection PyTypeChecker
class Settings:
    def __init__(self, seed_default_values: bool = True):
        self._settings_items = dict()
        if seed_default_values:
            self.seed_default_values()

    def add(self, item: SettingsItem):
        self._settings_items[item.settings_id] = item

    def serialize(self):
        serialized_settings_items = dict()
        for k in self._settings_items:
            print(self._settings_items[k].serialize())
            serialized_settings_items.update(self._settings_items[k].serialize())

        return json.dumps({
            "type": "object",
            "properties": serialized_settings_items,
            "requires": list(self._settings_items.keys())
        })

    def seed_default_values(self):
        self.add(SettingsItem(settings_type=SettingsItemType.NUMBER, settings_id="timeout", settings_title="Timeout"))


if __name__ == "__main__":
    settings = Settings()
    settings.add(SettingsItem(settings_type=SettingsItemType.STRING, settings_id="community_string", settings_title="Community String"))
    settings.add(SettingsItem(settings_type=SettingsItemType.NUMBER, settings_id="community_number", settings_title="Community Number"))

    print(settings.serialize())