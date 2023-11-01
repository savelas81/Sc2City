import sc2
from sc2.main import *
from sc2.bot_ai import BotAI
from sc2 import maps
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId
from bot_memory import UnitsInMemory
from MA_interface import MapAnalyserInterface


class Sc2City(BotAI):

    def __init__(self):
        self.memory   = UnitsInMemory(self)

    async def on_start(self):
        """on_start runs once in beginning of every game"""
        for scv in self.units(UnitTypeId.SCV):
            scv.attack(self.enemy_start_locations[0])
        self.MA = MapAnalyserInterface(self)

    async def on_step(self, iteration):
        self.memory.update_units_in_memory(enemy_units=self.all_enemy_units, our_units=(self.units|self.structures))
        self.MA.create_influence_maps(memory=self.memory)
        """creates infleunce maps from units in memory."""
        self.memory.enemy_units_in_memory()
        enemy_lost_minerals = self.memory.get_enemy_lost_minerals()
        enemy_lost_vespene = self.memory.get_enemy_lost_vespene()
        our_lost_minerals = self.memory.get_our_lost_minerals()
        our_lost_vespene = self.memory.get_our_lost_vespene()
        if enemy_lost_minerals > 0:
            print(enemy_lost_minerals)

    async def on_unit_destroyed(self, unit_tag: int):
        self.memory.forget_unit(unit_tag)
    async def on_end(self, game_result: Result):
        pass
