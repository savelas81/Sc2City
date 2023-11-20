from sc2.unit import Unit
from sc2.units import Units
import random
import numpy as np
from sc2.position import Pointlike, Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId
import copy
import math
import loguru


class ScoutManager:
    def __init__(self, ai=None):
        self.AI = ai
        self.scout_tag = None
        self.points_need_scouting = None
        self.next_point = None
        self.retreat = False
        self.debug = True
        self.scout_enemy_natural = True

    async def assign_unit_tag_scout(self, unit_tag: int):
        self.scout_tag = unit_tag
        if unit_tag in self.AI.units(UnitTypeId.SCV).tags:
            await self.AI.SCVManager.remove_unit_tag_from_lists(unit_tag=unit_tag)
            await self.AI.SCVManager.add_unit_tag_scout_list(unit_tag=unit_tag)

    async def remove_scout(self):
        if self.scout_tag:
            await self.AI.SCVManager.remove_unit_tag_from_lists(unit_tag=self.scout_tag)
        self.scout_tag = None
        self.points_need_scouting = None
        self.next_point = None
        self.retreat = False

    async def create_scouting_grid_for_enemy_main(self):
        """gets all grid points from enemy main base"""
        self.points_need_scouting = self.AI.MapAnalyzerInterface.MapData.where_all(self.AI.enemy_start_locations[0])[0].array

    async def move_scout(self):
        scout: Unit = self.AI.units.find_by_tag(self.scout_tag)
        if not scout:
            return
        if self.scout_enemy_natural:
            if not self.AI.is_visible(self.AI.enemy_expansions.natural):
                scout.move(self.AI.enemy_expansions.natural)
                return
            else:
                self.scout_enemy_natural = False
        if self.points_need_scouting is not None:
            if self.points_need_scouting.any():
                if scout.type_id == UnitTypeId.REAPER:
                    grid = copy.copy(self.AI.MapAnalyzerInterface.reaper_grid)
                elif scout.is_flying:
                    grid = copy.copy(self.AI.MapAnalyzerInterface.enemy_air_grid)
                else:
                    grid = copy.copy(self.AI.MapAnalyzerInterface.enemy_ground_grid)
                condition_list = [self.points_need_scouting == 1, self.points_need_scouting != 1]
                choice_list = [grid, math.inf]
                scouting_grid = np.select(condition_list, choice_list)
                lowest_cost_points = self.AI.MapAnalyzerInterface.MapData.lowest_cost_points_array(
                    from_pos=scout.position,
                    radius=500,
                    grid=scouting_grid)

                if self.AI.iteration % 4 == 0:
                    self.next_point = self.AI.MapAnalyzerInterface.MapData.closest_towards_point(points=lowest_cost_points,
                                                                                target=scout.position)
                if self.next_point is not None and self.next_point.any():
                    path = self.AI.MapAnalyzerInterface.MapData.pathfind(start=scout.position.rounded,
                                                        goal=self.next_point,
                                                        grid=grid,
                                                        sensitivity=3)
                    if path is not None and len(path) > 0:
                        scout.move(path[0])
                else:
                    loguru.logger.info(
                        f"No self.next_point {str(self.next_point)}"
                    )
                    return

    async def update_points_need_scouting(self):
        if self.points_need_scouting is None:
            return
        elif self.points_need_scouting.sum() == 0:
            self.points_need_scouting = None
            print("Scouting completed")
            await self.remove_scout()
            return
        else:
            visibility = np.transpose(self.AI.state.visibility.data_numpy)
            condition_list = [visibility == 2, visibility != 2]
            choice_list = [0, 1]
            remove_scouted_points = np.select(condition_list, choice_list)
            self.points_need_scouting *= remove_scouted_points
        if self.debug:
            for x in range(0, self.points_need_scouting.shape[0]):
                for y in range(0, self.points_need_scouting.shape[1]):
                    if self.points_need_scouting[x, y] == 1:
                        p= Point2((x, y))
                        h2 = self.AI.get_terrain_z_height(p)
                        pos = Point3((p.x, p.y, h2))
                        size = 0.45
                        p0 = Point3((pos.x - size, pos.y - size, pos.z + size))
                        p1 = Point3((pos.x + size, pos.y + size, pos.z - 0))
                        c = Point3((255, 0, 0))
                        self.AI.client.debug_box_out(p0, p1, color=c)
