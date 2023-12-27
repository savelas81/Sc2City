import enum
import os

from .config import Paths


class Strategies(enum.Enum):
    def __str__(self):
        return os.path.join(self._base_path.value, self.value)


class Openings(Strategies):
    _base_path = Paths.OPENINGS.value
    TEST = "test.json"


class MidGames(Strategies):
    _base_path = Paths.MID_GAMES.value
    TEST = "test.json"


class LateGames(Strategies):
    _base_path = Paths.LATE_GAMES.value
    TEST = "test.json"


class Reactionary(Strategies):
    _base_path = Paths.REACTIONARY.value
    TEST = "test.json"
