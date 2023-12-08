from typing import Optional

from sc2.bot_ai import BotAI
from sc2.data import Race
from sc2.unit import Unit

from utils import Settings, OrderType
from game_objects import Strategy, Order
from managers import (
    HistoryAnalyzer,
    MapAnalyzer,
    MacroManager,
    MicroManager,
    BuildOrderManager,
    UnitsManager,
)


class Sc2City(BotAI):
    race = Race.Terran

    def __init__(self, settings: Settings) -> None:
        # Settings
        self.settings = settings
        self.debug = settings.debug

        # Managers
        self.map_analyzer: Optional[MapAnalyzer] = None
        self.history_analyzer = HistoryAnalyzer()  # TODO: Add history analyzer
        self.macro_manager = MacroManager(self)
        self.micro_manager = MicroManager(self)
        self.build_order_manager = BuildOrderManager(self)
        self.units_manager = UnitsManager(self)

        # State
        self.iteration: int = 0
        self.current_strategy: Optional[Strategy] = None
        self.queues: dict[OrderType, list[Order]] = {
            OrderType.STRUCTURE: [],
            OrderType.UNIT: [],
            OrderType.TECH: [],
        }
        self.mineral_collector_dict: dict[int, int] = {}
        self.vespene_collector_dict: dict[int, int] = {}
        # TODO: Implement army logic with scripts. Eg: army = {soldiers: [(Unit, Script)], squads: [(Squad, Script)], scouts: [(Scout, Script)]}
        self.scouts: list[Unit] = []
        # TODO: Merge this with scouting logic in micro manager
        self.pending_scouting_points = None

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

    async def on_building_construction_complete(self, unit: Unit):
        self.macro_manager.production_complete(unit, OrderType.STRUCTURE)

    async def on_unit_created(self, unit: Unit) -> None:
        self.macro_manager.production_complete(unit, OrderType.UNIT)

    async def on_unit_destroyed(self, unit_tag: int) -> None:
        self.map_analyzer.forget_unit(unit_tag)
