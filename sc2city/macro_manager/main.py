import json

from sc2.bot_ai import BotAI
from utils import strategies


class MacroManager:
    openings = strategies.Openings
    mid_games = strategies.MidGames
    late_games = strategies.LateGames
    reactionary = strategies.Reactionary

    def __init__(self, bot: BotAI):
        self.bot = bot

    def choose_first_strategy(self):
        opening = self.__choose_opening()
        self.bot.current_strategy = opening

    def __choose_opening(self):
        # Replace with logic to choose opening
        opening_file = str(self.openings.TEST)
        opening = self.__load_strategy(opening_file)
        return opening

    def __load_strategy(self, strategy_file: str):
        try:
            with open(strategy_file, "r") as f:
                strategy = json.load(f)
            return strategy
        except (OSError, IOError) as e:
            print("Strategy file not found.")
            print(e)
