import enum
import json
from loguru import logger
from dataclasses import dataclass


class Paths(enum.Enum):
    OPENINGS = "data/strategies/openings/"
    MID_GAMES = "data/strategies/mid_games/"
    LATE_GAMES = "data/strategies/late_games/"
    REACTIONARY = "data/strategies/reactionary/"
    ONE_BASE = "data/building_placements/one_base/"
    PROXY = "data/building_placements/proxy/"
    STANDARD = "data/building_placements/standard/"


class BuildTypes(enum.Enum):
    ONE_BASE = Paths.ONE_BASE.value
    STANDARD = Paths.STANDARD.value
    PROXY = Paths.PROXY.value


class Status(enum.Enum):
    PENDING = 0
    PLACEHOLDER = 1
    STARTED = 2
    INTERRUPTED = 3
    FINISHED = 4


class OrderType(enum.Enum):
    STRUCTURE = 0
    UNIT = 1
    TECH = 2
    ACTION = 3


@dataclass
class Settings:
    """
    Class representing the settings for the bot behavior.
    """

    tournaments: bool = True
    debug: bool = False
    vs_bots: bool = True

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(**dct)


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
            settings = json.load(f)
        return Settings.from_dict(settings)
    except Exception as e:
        logger.error(
            f"An error occurred while loading settings: {e}. Using default settings."
        )
        return Settings()
