import enum
import os


class Paths(enum.Enum):
    OPENINGS = "data/strategies/openings/"
    MID_GAMES = "data/strategies/mid_games/"
    LATE_GAMES = "data/strategies/late_games/"
    REACTIONARY = "data/strategies/reactionary/"


class Strategy(enum.Enum):
    def __str__(self):
        return os.path.join(self._base_path.value, self.value)


class Openings(Strategy):
    _base_path = Paths.OPENINGS.value
    TEST = "test.json"


class MidGames(Strategy):
    _base_path = Paths.MID_GAMES.value
    TEST = "test.json"


class LateGames(Strategy):
    _base_path = Paths.LATE_GAMES.value
    TEST = "test.json"


class Reactionary(Strategy):
    _base_path = Paths.REACTIONARY.value
    TEST = "test.json"
