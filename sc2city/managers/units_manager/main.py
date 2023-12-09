import math
import numpy as np
from loguru import logger
from copy import copy
from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId

if TYPE_CHECKING:
    from Sc2City import Sc2City


# TODO: Implement army logic with scripts where the army distribution is decided by the micro manager and the scripts are executed here
class UnitsManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.next_point = None  # TODO: Remove this when refactoring scouting logic

    def give_orders(self) -> None:
        # TODO: Add methods to execute other tasks
        if self.bot.scouts:
            self.__move_scout()

    def __move_scout(self) -> None:
        # TODO: Add a marker to scripts with no new information to avoid actions being executed in every frame
        scout: Unit = self.bot.units.find_by_tag(
            self.bot.scouts[0].tag
        )  # Is it really necessary to search by tag when I have the unit?
        if not scout:
            logger.error("Could not find scout by tag")
            return
        if self.bot.micro_manager.pending_scouting_locations:
            scout.move(self.bot.micro_manager.pending_scouting_locations[0])
            return

        if self.bot.pending_scouting_points is not None:
            if self.bot.pending_scouting_points.any():
                if scout.type_id == UnitTypeId.REAPER:
                    grid = copy(self.bot.map_analyzer.reaper_grid)
                elif scout.is_flying:
                    grid = copy(self.bot.map_analyzer.enemy_air_grid)
                else:
                    grid = copy(self.bot.map_analyzer.enemy_ground_grid)
                condition_list = [
                    self.bot.pending_scouting_points == 1,
                    self.bot.pending_scouting_points != 1,
                ]
                choice_list = [grid, math.inf]
                scouting_grid = np.select(condition_list, choice_list)
                lowest_cost_points = (
                    self.bot.map_analyzer.map_data.lowest_cost_points_array(
                        from_pos=scout.position, radius=500, grid=scouting_grid
                    )
                )

                if self.bot.iteration % 4 == 0:
                    self.next_point = (
                        self.bot.map_analyzer.map_data.closest_towards_point(
                            points=lowest_cost_points, target=scout.position
                        )
                    )
                if self.next_point is not None and self.next_point.any():
                    path = self.bot.map_analyzer.map_data.pathfind(
                        start=scout.position.rounded,
                        goal=self.next_point,
                        grid=grid,
                        sensitivity=3,
                    )
                    if path is not None and len(path) > 0:
                        scout.move(path[0])
                else:
                    # logger.info(f"No self.next_point {str(self.next_point)}")
                    return
