import json
from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.position import Point2

from utils import strategies, Status, OrderType
from game_objects import Strategy, ScoutTime
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
        self.pending_scv_scouts: list[ScoutTime] = []
        self.queue_manager = QueueManager(bot)
        self.map_file = None

    def choose_first_strategy(self) -> None:
        self.__set_map_filename()
        opening = self.__choose_opening()
        self.bot.current_strategy = Strategy.from_dict(opening, self.map_file)
        self.queue_manager.set_starting_queues()
        # TODO: Create method to handle SCV scouts
        self.pending_scv_scouts = [
            s for s in self.bot.current_strategy.scout_times if s.id == "SCV"
        ]

    def update_strategy(self) -> None:
        # TODO: Add logic to update strategy based on game state
        # TODO: Add logic to make decisions outside of imported strategies
        self.queue_manager.update_queues()
        if self.pending_scv_scouts:
            self.__update_scv_scouts()

    def unit_created(self, unit: Unit) -> None:
        order = next(
            (
                order
                for order in self.bot.queues[OrderType.UNIT]
                if order.id == unit.type_id and order.status == Status.PENDING
            ),
            None,
        )
        if order is not None:
            order.status = Status.FINISHED
        else:
            # TODO: Add logic to handle units that are not in the queue
            print(f"Unit {unit.type_id} not found in queue")

    def __update_scv_scouts(self) -> None:
        # TODO: Add logic to select the best scv scout position
        position = self.bot.start_location
        for scout in self.pending_scv_scouts:
            if self.bot.time < scout.time:
                continue

            scv = self.__select_scv_scout(position)
            if scv is None:
                print("No available SCVs to scout")
                return

            self.bot.scouts.append(scv)
            del self.bot.mineral_collector_dict[scv.tag]
            self.pending_scv_scouts.remove(scout)

    def __select_scv_scout(self, position: Point2) -> Unit | None:
        # TODO: Add more robust logic to select other types of SCV scouts aside from mineral collectors
        worker = next(
            (
                w
                for w in self.bot.workers.sorted(lambda x: x.distance_to(position))
                if w.tag in self.bot.mineral_collector_dict
                and not w.is_carrying_resource
            ),
            None,
        )
        return worker

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

    def __set_map_filename(self) -> None:
        # This function should only run at the start of the game to discover the correct set of map files
        map_name = self.bot.game_info.map_name
        starting_location = self.bot.start_location
        self.map_file = map_name + str(starting_location) + ".json"
