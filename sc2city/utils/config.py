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
    STARTED = 1
    INTERRUPTED = 2
    FINISHED = 3


class OrderType(enum.Enum):
    STRUCTURE = 0
    PRODUCTION = 1
    ACTION = 2
    SCV_ACTION = 3


class SCVAssignment(enum.Enum):
    MINERALS = 0
    VESPENE = 1
    BUILD = 2
    SCOUT = 3
    REPAIR = 4
    ARMY = 5
    NONE = 6


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
        """
        Load settings from a dictionary.
        """
        return cls(**dct)

    @classmethod
    def from_json_file(cls, settings_file: str = "settings.json"):
        """
        Load settings from a JSON file.

        Args:
            settings_file (str): The path to the JSON file containing the settings. Default is "settings.json".
        """
        try:
            with open(settings_file) as f:
                settings = json.load(f)
            return cls.from_dict(settings)
        except Exception as e:
            logger.error(
                f"An error occurred while loading settings: {e}. Using default settings."
            )
            return cls()
