import json
from typing import Optional

from sc2.bot_ai import BotAI
from sc2.data import Race
from sc2.unit import Unit

from history_analyzer import HistoryAnalyzer
from map_analyzer import MapAnalyzer
from macro_manager import MacroManager
from micro_manager import MicroManager
from build_order_manager import BuildOrderManager
from units_manager import UnitsManager


class Sc2City(BotAI):
    race = Race.Terran
    settings_file = "settings.json"

    def __init__(self):
        # Settings
        self.settings: dict = self.__load_settings()
        self.debug = self.settings.get("debug", False)

        # Managers
        self.map_analyzer: Optional[MapAnalyzer] = None
        self.history_analyzer = HistoryAnalyzer()  # TODO: Add history analyzer
        self.macro_manager = MacroManager(self)
        self.micro_manager = MicroManager(self)
        self.build_order_manager = BuildOrderManager(self)
        self.units_manager = UnitsManager(self)

        # State
        self.iteration: int = 0
        self.current_strategy: Optional[dict] = None
        self.mineral_collector_dict: dict[int, int] = {}
        self.vespene_collector_dict: dict[int, int] = {}
        # TODO: Implement army logic with scripts. Eg: army = {soldiers: [(Unit, Script)], squads: [(Squad, Script)], scouts: [(Scout, Script)]}
        self.scouts: list[Unit] = []
        # TODO: Merge this with scouting logic in micro manager
        self.pending_scouting_points = None

    def __load_settings(self):
        with open(self.settings_file) as f:
            settings = json.load(f)
        return settings

    async def on_start(self) -> None:
        self.client.game_step = 2
        self.macro_manager.choose_first_strategy()
        self.build_order_manager.execute_frame_zero()

        self.map_analyzer = MapAnalyzer(self)
        await self.map_analyzer.get_initial_map_info()
        self.micro_manager.set_initial_unit_scripts()

    async def on_step(self, iteration: int) -> None:
        self.iteration = iteration

        self.map_analyzer.update_map_info()
        self.macro_manager.update_strategy()
        self.micro_manager.update_unit_scripts()

        # TODO: Implement synchronous execution of managers
        self.build_order_manager.execute_strategy()
        self.units_manager.give_orders()

    async def on_unit_destroyed(self, unit_tag: int) -> None:
        self.map_analyzer.forget_unit(unit_tag)
