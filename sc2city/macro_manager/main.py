import json
from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.position import Point2

from utils import strategies
from .structure_queue_manager import StructureQueueManager
from .unit_queue_manager import UnitQueueManager

if TYPE_CHECKING:
    from Sc2City import Sc2City


class MacroManager:
    openings = strategies.Openings
    mid_games = strategies.MidGames
    late_games = strategies.LateGames
    reactionary = strategies.Reactionary

    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.pending_scv_scouts: list[dict] = []
        self.structure_queue_manager = StructureQueueManager(bot)
        self.unit_queue_manager = UnitQueueManager(bot)

    def choose_first_strategy(self) -> None:
        opening = self.__choose_opening()
        self.bot.current_strategy = opening
        self.pending_scv_scouts = [
            s for s in self.bot.current_strategy.get("scouts") if s.get("id") == "SCV"
        ]

    def update_strategy(self) -> None:
        # TODO: Add logic to update strategy based on game state
        # TODO: Add logic to make decisions outside of imported strategies

        if self.pending_scv_scouts:
            self.__update_scv_scouts()

    def __update_scv_scouts(self) -> None:
        # TODO: Add logic to select the best scv scout position
        position = self.bot.start_location
        for scout in self.pending_scv_scouts:
            if self.bot.time < scout.get("time"):
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
