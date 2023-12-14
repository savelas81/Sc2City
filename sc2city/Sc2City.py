from typing import Optional

from sc2.bot_ai import BotAI
from sc2.data import Race
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId

from utils import Settings
from game_objects import Strategy, Order, Base, Workers
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
        self.queue: list[Order] = []
        self.scv_tags: set[int] = set()
        self.scvs = Workers()
        self.bases: list[Base] = []

        # TODO: Implement army logic with scripts. Eg: army = {soldiers: [(Unit, Script)], squads: [(Squad, Script)], scouts: [(Scout, Script)]}
        # TODO: Merge this with scouting logic in micro manager
        self.pending_scouting_points = None

    async def on_start(self) -> None:
        self.client.game_step = 2
        self.macro_manager.choose_first_strategy()
        self.build_order_manager.execute_frame_zero()

        self.map_analyzer = MapAnalyzer(self)
        await self.map_analyzer.get_initial_map_info()
        self.micro_manager.set_initial_unit_scripts()

        # Workaround for weird SCV/Refinery behavior
        self.scv_tags = {worker.tag for worker in self.workers}

    async def on_step(self, iteration: int) -> None:
        self.iteration = iteration

        self.map_analyzer.update_map_info()
        self.macro_manager.update_strategy()
        self.micro_manager.update_unit_scripts()

        await self.build_order_manager.execute_strategy()
        self.units_manager.give_orders()

    async def on_building_construction_started(self, unit: Unit):
        self.build_order_manager.building_construction_started(unit)

    async def on_building_construction_complete(self, unit: Unit):
        self.build_order_manager.production_complete(unit)

    # TODO: Implement this
    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        pass

    # TODO: Implement this
    async def on_upgrade_complete(self, upgrade: UpgradeId):
        pass

    async def on_unit_created(self, unit: Unit) -> None:
        # Workaround for weird SCV/Refinery behavior
        if unit.type_id == UnitTypeId.SCV:
            if unit.tag in self.scv_tags:
                return
            else:
                self.scv_tags.add(unit.tag)
        self.build_order_manager.production_complete(unit)

    async def on_unit_destroyed(self, unit_tag: int) -> None:
        self.map_analyzer.forget_unit(unit_tag)
