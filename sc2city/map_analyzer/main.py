import numpy
from typing import TYPE_CHECKING, Optional

from sc2.position import Point2

from .map_data import MapData

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

        # Grids
        self.enemy_ground_to_air_grid: Optional[numpy.ndarray] = None
        self.enemy_ground_grid: Optional[numpy.ndarray] = None
        self.enemy_air_grid: Optional[numpy.ndarray] = None
        self.reaper_grid: Optional[numpy.ndarray] = None

    async def get_expansions(self) -> None:
        expansions = self.bot.expansion_locations_list
        starting_location = self.bot.start_location
        enemy_start_location = self.bot.enemy_start_locations[0]

        distances = await self.__calculate_path_distances(starting_location, expansions)
        enemy_distances = await self.__calculate_path_distances(
            enemy_start_location, expansions
        )

        self.expansions = [expansion for _, expansion in distances]
        self.enemy_expansions = [expansion for _, expansion in enemy_distances]

    def update_influence_maps(self) -> None:
        # Constructing Grids:
        self.enemy_ground_to_air_grid: numpy.ndarray = self.map_data.get_clean_air_grid(
            default_weight=1
        )
        self.enemy_ground_grid: numpy.ndarray = self.map_data.get_pyastar_grid(
            default_weight=1
        )
        self.enemy_air_grid: numpy.ndarray = self.map_data.get_pyastar_grid(
            default_weight=1
        )

        self.reaper_grid: numpy.ndarray = self.map_data.get_climber_grid(
            default_weight=1
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
