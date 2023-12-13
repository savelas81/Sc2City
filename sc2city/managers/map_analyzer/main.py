import numpy as np
import copy
from typing import TYPE_CHECKING, Optional

from sc2.position import Point2, Point3

from third_party_code import MapData
from .memory_manager import MemoryManager

if TYPE_CHECKING:
    from Sc2City import Sc2City


class MapAnalyzer:
    EXTRA_GROUND_DISTANCE: int = 3
    EXTRA_AIR_DISTANCE: int = 3

    def __init__(self, bot: "Sc2City"):
        self.bot = bot

        self.expansions = []
        self.enemy_expansions = []
        self.map_data = MapData(bot=bot, loglevel="INFO")
        self.memory_manager = MemoryManager(bot)

        # Grids
        self.enemy_ground_to_air_grid: Optional[np.ndarray] = None
        self.enemy_ground_grid: Optional[np.ndarray] = None
        self.enemy_air_grid: Optional[np.ndarray] = None
        self.reaper_grid: Optional[np.ndarray] = None

    async def get_initial_map_info(self) -> None:
        await self.__get_expansions()
        self.__set_scouting_grid_for_enemy_main()
        self.__add_to_pending_scouting_points(
            position=self.enemy_expansions[0], radius=2
        )

    def remember_units(self) -> None:
        self.memory_manager.remember_units()

    def forget_unit(self, unit_tag: int) -> None:
        self.memory_manager.forget_unit(unit_tag)

    def update_map_info(self) -> None:
        # TODO: Add logic to update all relevant map information
        self.__update_influence_maps()
        if self.bot.pending_scouting_points is not None:
            self.__update_pending_scouting_points()

    def __add_to_pending_scouting_points(self, position: Point2, radius: int = 1):
        grid = copy.copy(self.bot.pending_scouting_points)
        grid = self.map_data.add_cost(
            position=position, radius=radius, grid=grid, weight=1
        )
        condition_list = [grid >= 1, grid < 1]
        choice_list = [1, 0]
        self.bot.pending_scouting_points = np.select(condition_list, choice_list)

    def __set_scouting_grid_for_enemy_main(self) -> None:
        """gets all grid points from enemy main base"""
        # TODO: Improve typing for this method
        self.bot.pending_scouting_points = self.map_data.where_all(
            self.bot.enemy_start_locations[0]
        )[0].array

    async def __get_expansions(self) -> None:
        expansions = self.bot.expansion_locations_list
        starting_location = self.bot.start_location
        enemy_start_location = self.bot.enemy_start_locations[0]

        distances = await self.__calculate_path_distances(starting_location, expansions)
        enemy_distances = await self.__calculate_path_distances(
            enemy_start_location, expansions
        )

        self.expansions = [expansion for _, expansion in distances]
        self.enemy_expansions = [expansion for _, expansion in enemy_distances]

    def __update_pending_scouting_points(self) -> None:
        # TODO: Add flexibility for adding any number of scouts and scouting targets
        if self.bot.pending_scouting_points.sum() == 0:
            self.bot.pending_scouting_points = None
            return
        else:
            visibility = np.transpose(self.bot.state.visibility.data_numpy)
            condition_list = [visibility == 2, visibility != 2]
            choice_list = [0, 1]
            remove_scouted_points = np.select(condition_list, choice_list)
            self.bot.pending_scouting_points *= remove_scouted_points
        if self.bot.debug:
            for x in range(0, self.bot.pending_scouting_points.shape[0]):
                for y in range(0, self.bot.pending_scouting_points.shape[1]):
                    if self.bot.pending_scouting_points[x, y] == 1:
                        p = Point2((x, y))
                        h2 = self.bot.get_terrain_z_height(p)
                        pos = Point3((p.x, p.y, h2))
                        size = 0.45
                        p0 = Point3((pos.x - size, pos.y - size, pos.z + size))
                        p1 = Point3((pos.x + size, pos.y + size, pos.z - 0))
                        c = Point3((255, 0, 0))
                        self.bot.client.debug_box_out(p0, p1, color=c)

    def __update_influence_maps(self) -> None:
        # Constructing Grids:
        self.enemy_ground_to_air_grid: np.ndarray = self.map_data.get_clean_air_grid(
            default_weight=1
        )
        self.enemy_ground_grid: np.ndarray = self.map_data.get_pyastar_grid(
            default_weight=1
        )
        self.enemy_air_grid: np.ndarray = self.map_data.get_pyastar_grid(
            default_weight=1
        )

        self.reaper_grid: np.ndarray = self.map_data.get_climber_grid(default_weight=1)

        self.memory_manager.remember_units()
        for enemy_unit in self.memory_manager.enemy_unit_tag_to_unit_object.values():
            # Debugging:
            if self.bot.debug:
                self.bot.client.debug_sphere_out(
                    p=enemy_unit, r=enemy_unit.radius, color=(255, 0, 0)
                )

            if enemy_unit.can_attack_ground:
                enemy_total_range: float = (
                    enemy_unit.radius
                    + enemy_unit.ground_range
                    + self.EXTRA_GROUND_DISTANCE
                )

                (
                    self.enemy_ground_grid,
                    self.reaper_grid,
                ) = self.map_data.add_cost_to_multiple_grids(
                    position=enemy_unit.position,
                    radius=enemy_total_range,
                    grids=[self.enemy_ground_grid, self.reaper_grid],
                    weight=enemy_unit.ground_dps,
                )
            elif enemy_unit.can_attack_air:
                enemy_total_range: float = (
                    enemy_unit.radius + enemy_unit.air_range + self.EXTRA_AIR_DISTANCE
                )

                if enemy_unit.is_flying:
                    self.enemy_air_grid = self.map_data.add_cost(
                        position=enemy_unit.position,
                        radius=enemy_total_range,
                        grid=self.enemy_air_grid,
                        weight=enemy_unit.air_dps,
                    )
                else:
                    (
                        self.enemy_ground_to_air_grid,
                        self.enemy_air_grid,
                    ) = self.map_data.add_cost_to_multiple_grids(
                        position=enemy_unit.position,
                        radius=enemy_total_range,
                        grids=[self.enemy_ground_to_air_grid, self.enemy_air_grid],
                        weight=enemy_unit.air_dps,
                    )

                if self.bot.debug:
                    # Variables:
                    color: Point3 = Point3((201, 168, 79))
                    size: int = 14

                    for x, y in zip(*np.where(self.enemy_ground_grid > 1)):
                        height: float = self.bot.get_terrain_z_height(
                            self.bot.start_location
                        )

                        position: Point3 = Point3((x, y, height))

                        if self.enemy_ground_grid[x, y] == np.inf:
                            continue

                        value: int = int(self.enemy_ground_grid[x, y])
                        self.bot.client.debug_text_world(
                            text=str(value), pos=position, color=color, size=size
                        )

    async def __calculate_path_distances(
        self, starting_position: Point2, goals: list[Point2]
    ) -> list[tuple[float, Point2]]:
        distances = []
        for goal in goals:
            path_distance = await self.bot.client.query_pathing(starting_position, goal)
            if path_distance is not None:
                distances.append((path_distance, goal))
        distances.sort(key=lambda x: x[0])
        return distances
