from enum import Enum


class SettingsItemType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ENUM = "enum"


# noinspection PyTypeChecker
class SettingsItem:
    def __init__(self, settings_type: SettingsItemType, settings_id: str, settings_title: str, settings_enum_items: list = None):
        self._settings_type = settings_type
        self._settings_id = settings_id
        self._settings_title = settings_title
        self._settings_enum_items = settings_enum_items

    def serialize(self):
        return_data = {}
        additional = {}
        if self._settings_type == SettingsItemType.ENUM:
            additional["enum"] = self._settings_enum_items
            self._settings_type = SettingsItemType.STRING
        return_data[self._settings_id] = {"type": self._settings_type.value, "title": self._settings_title}
        return_data.update(additional)
        return return_data


# noinspection PyTypeChecker
class Settings:
    def __init__(self):
        self._settings_items = dict()

    def add(self, item: SettingsItem):
        self._settings_items.update(item.serialize())

    def serialize(self):
        return {
            "type": "object",
            "properties": self._settings_items,
            "requires": self._settings_items.keys()
        }


if __name__ == "__main__":
    settings = Settings()
    settings.add(SettingsItem(settings_type=SettingsItemType.STRING, settings_id="community_string", settings_title="Community String"))
    settings.add(SettingsItem(settings_type=SettingsItemType.NUMBER, settings_id="community_number", settings_title="Community Number"))

    print(settings.serialize())