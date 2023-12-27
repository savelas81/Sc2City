import json
from typing import TYPE_CHECKING

from game_objects import Order, Strategy
from utils import Status, strategies

from .queue_manager import QueueManager

if TYPE_CHECKING:
    from Sc2City import Sc2City


class MacroManager:
    openings = strategies.Openings
    mid_games = strategies.MidGames
    late_games = strategies.LateGames
    reactionary = strategies.Reactionary

    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.queue_manager = QueueManager(bot)
        self.map_file = None
        self.order_handlers = {
            Status.PENDING: self.__handle_pending_order,
            Status.STARTED: self.__handle_started_order,
            Status.INTERRUPTED: self.__handle_interrupted_order,
            Status.FINISHED: self.__handle_finished_order,
        }

    def choose_first_strategy(self) -> None:
        self.__set_map_filename()
        opening = self.__choose_opening()
        self.bot.current_strategy = Strategy.from_dict(opening, self.map_file)
        self.queue_manager.start_new_queue(self.bot.current_strategy.build_order)

    # TODO: Add logic to update strategy based on game state
    # TODO: Add logic to make decisions outside of imported strategies
    # TODO: Add logic for deciding what to do with each order
    def update_strategy(self) -> None:
        self.bot.economy.update()
        for order in self.bot.queue:
            if order.age == 0:
                break
            self.order_handlers[order.status](order)
        self.queue_manager.update_queue()

    def __handle_pending_order(self, order: Order) -> None:
        pass

    def __handle_started_order(self, order: Order) -> None:
        pass

    def __handle_interrupted_order(self, order: Order) -> None:
        pass

    def __handle_finished_order(self, order: Order) -> None:
        self.bot.queue.remove(order)

    def __choose_opening(self) -> dict:
        # TODO: Replace with logic to choose opening
        opening_file = str(self.mid_games.TEST)
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

    def __set_map_filename(self) -> None:
        # This function should only run at the start of the game to discover the correct set of map files
        map_name = self.bot.game_info.map_name
        starting_location = self.bot.start_location
        self.map_file = map_name + str(starting_location) + ".json"
