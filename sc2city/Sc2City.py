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
from opener_manager import OpenerManager
from scv_manager import ScvManager
from scout_manager import ScoutManager
from cache_first_frame import EnemyExpansions
from sc2.ids.ability_id import AbilityId


class Sc2City(BotAI):

    def __init__(self):
        self.raw_affects_selection = False  # True = Fast gameplay
        self.memory = UnitsInMemory(self)
        self.strategy_manager = StrategyManager(self)
        self.building_placements = BuildingPlacementSolver(self)
        self.opener_manager = OpenerManager(self)
        self.scv_manager = ScvManager(self)
        self.scout_manager = ScoutManager(self)
        self.enemy_expansions = EnemyExpansions(self)
        self.iteration = 0
        self.send_scv_scout = True

    async def on_start(self):
        """on_start runs once in beginning of every game"""
        self.client.game_step = 8  #  2 for ladder 4 for testing
        self.building_placements.load_data()
        self.MA = MapAnalyserInterface(self)
        await self.scv_manager.worker_split_frame_zero()
        await self.enemy_expansions.cache_enemy_expansions()


    async def on_step(self, iteration):
        self.iteration = iteration
        self.memory.update_units_in_memory(
            enemy_units=self.all_enemy_units, our_units=(self.units | self.structures)
        )
        """creates influence maps from units in memory."""
        self.MA.create_influence_maps(memory=self.memory)
        # enemy_lost_minerals = self.memory.get_enemy_lost_minerals()
        # enemy_lost_vespene = self.memory.get_enemy_lost_vespene()
        # our_lost_minerals = self.memory.get_our_lost_minerals()
        # our_lost_vespene = self.memory.get_our_lost_vespene()
        await self.strategy_manager.run_strategy()
        await self.scout_manager.update_points_need_scouting()
        await self.scout_manager.move_scout()
        await self.scv_manager.move_scvs()
        if self.send_scv_scout and self.time >= 37:
            self.send_scv_scout = False
            await self.scout_manager.create_scouting_grid_for_enemy_main()
            await self.scout_manager.assign_unit_tag_scout(self.workers.random.tag)


        """quick fix for mules"""
        for orbital in self.townhalls(UnitTypeId.ORBITALCOMMAND):
            if orbital.energy >= 50:
                mfs = self.mineral_field.closer_than(10, orbital)
                mf = mfs.random
                orbital(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf)
        """quick fix to lower depots"""
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT):
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

    async def on_unit_destroyed(self, unit_tag: int):
        self.memory.forget_unit(unit_tag)

    async def on_end(self, game_result: Result):
        pass
