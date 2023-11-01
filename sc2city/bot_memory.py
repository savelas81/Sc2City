from sc2.constants import *
from sc2.units import Units
from sc2.unit import Unit
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
import sc2
from sc2.game_data import Cost



class UnitsInMemory:
    def __init__(self, ai=None):
        self.ai = ai
        # self.enemy_units_in_memory = Units([], self.ai)
        self.enemy_units_in_memory_by_tag = {}
        self.our_units_in_memory_by_tag = {}
        self.debug_timer = 0
        self.killed_enemy_units  = Units([], self.ai)
        self.lost_friendly_units = Units([], self.ai)

    def update_units_in_memory(self, enemy_units, our_units):
        """This needs to be updated every step"""
        for unit in enemy_units:
            if unit.tag in self.enemy_units_in_memory_by_tag.keys():
                self.enemy_units_in_memory_by_tag.update({unit.tag: unit})
            else:
                self.enemy_units_in_memory_by_tag[unit.tag] = unit
        for unit in our_units:
            if unit.tag in self.our_units_in_memory_by_tag.keys():
                self.our_units_in_memory_by_tag.update({unit.tag: unit})
            else:
                self.our_units_in_memory_by_tag[unit.tag] = unit

    def forget_unit(self, unit_tag):
        if unit_tag in self.enemy_units_in_memory_by_tag:
            unit = self.enemy_units_in_memory_by_tag.pop(unit_tag)
            self.killed_enemy_units.append(unit)
        elif unit_tag in self.our_units_in_memory_by_tag:
            unit = self.our_units_in_memory_by_tag.pop(unit_tag)
            self.lost_friendly_units.append(unit)

    def enemy_units_in_memory(self) -> Units:
        return self.enemy_units_in_memory_by_tag.values()

    def get_enemy_lost_minerals(self) -> int:
        minerals = 0
        value: Cost
        for unit in self.killed_enemy_units:
            value = self.ai.calculate_unit_value(unit.type_id)
            minerals += value.minerals
        return minerals
    def get_enemy_lost_vespene(self) -> int:
        vespene = 0
        value: Cost
        for unit in self.killed_enemy_units:
            value = self.ai.calculate_unit_value(unit.type_id)
            vespene += value.vespene
        return vespene

    def get_our_lost_minerals(self) -> int:
        minerals = 0
        value: Cost
        for unit in self.lost_friendly_units:
            value = self.ai.calculate_unit_value(unit.type_id)
            minerals += value.minerals
        return minerals
    def get_our_lost_vespene(self) -> int:
        vepene = 0
        value: Cost
        for unit in self.lost_friendly_units:
            value = self.ai.calculate_unit_value(unit.type_id)
            vepene += value.minerals
        return vepene
