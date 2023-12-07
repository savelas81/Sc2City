import json
from loguru import logger
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Class representing the settings for the bot behavior.
    """

    tournaments: bool = True
    debug: bool = False
    vs_bots: bool = True


class SettingsDecoder(json.JSONDecoder):
    def object_hook(self, dct):
        return Settings(**dct)


def load_settings(settings_file: str = "settings.json") -> Settings:
    """
    Load the settings from a JSON file.

    Args:
        settings_file (str): The path to the settings file. Default is "settings.json".

    Returns:
        Settings: The loaded settings.

    Raises:
        Exception: If an error occurs while loading the settings, a default settings object is returned.
    """
    try:
        with open(settings_file) as f:
            settings: Settings = json.load(f, cls=SettingsDecoder)
        return settings
    except Exception as e:
        logger.error(
            f"An error occurred while loading settings: {e}. Using default settings."
        )
        return Settings()
