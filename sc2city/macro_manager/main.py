import json
from typing import TYPE_CHECKING

from utils import strategies

if TYPE_CHECKING:
    from Sc2City import Sc2City


class MacroManager:
    openings = strategies.Openings
    mid_games = strategies.MidGames
    late_games = strategies.LateGames
    reactionary = strategies.Reactionary

    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def choose_first_strategy(self) -> None:
        opening = self.__choose_opening()
        self.bot.current_strategy = opening

    def __choose_opening(self) -> dict:
        # TODO: Replace with logic to choose opening
        opening_file = str(self.openings.TEST)
        opening = self.__load_strategy(opening_file)
        return opening

    def __load_strategy(self, strategy_file: str) -> dict:
        try:
            with open(strategy_file, "r") as f:
                strategy = json.load(f)
            return strategy
        except (OSError, IOError) as e:
            # TODO: Add a default strategy file to fallback on
            print("Strategy file not found.")
            print(e)
