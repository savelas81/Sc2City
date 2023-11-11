import sc2
from sc2.data import Result
from sc2.main import *
from sc2.bot_ai import BotAI
from sc2 import maps
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId
from bot_memory import UnitsInMemory
from MA_interface import MapAnalyserInterface
from strategy_manager import StrategyManager
from building_placements import BuildingPlacementSolver


class Sc2City(BotAI):

    def __init__(self):
        self.memory = UnitsInMemory(self)
        self.strategy_manager = StrategyManager(self)
        self.building_placements = BuildingPlacementSolver

    async def on_start(self):
        """on_start runs once in beginning of every game"""
        self.MA = MapAnalyserInterface(self)

    async def on_step(self, iteration):
        self.memory.update_units_in_memory(enemy_units=self.all_enemy_units, our_units=(self.units|self.structures))
        """creates influence maps from units in memory."""
        self.MA.create_influence_maps(memory=self.memory)
        # enemy_lost_minerals = self.memory.get_enemy_lost_minerals()
        # enemy_lost_vespene = self.memory.get_enemy_lost_vespene()
        # our_lost_minerals = self.memory.get_our_lost_minerals()
        # our_lost_vespene = self.memory.get_our_lost_vespene()
        self.strategy_manager.run_strategy()

    async def on_unit_destroyed(self, unit_tag: int):
        self.memory.forget_unit(unit_tag)

    async def on_end(self, game_result: Result):
        pass
