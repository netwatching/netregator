from enum import Enum


class SettingsItemType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ENUM = "enum"

class Settings:
    pass

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

if __name__ == "__main__":
    s = SettingsItem(settings_type=SettingsItemType.STRING, settings_id="test", settings_title="MyTestTile")

    print(s.serialize())