# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > Position:
from sc2.position import Point3

# MapAnalyzer:
# > MapData:
from sc2city.MapAnalyzer.MapData import MapData

# Typing:
import typing

# Numpy:
import numpy

# Classes:

"""
* Interface class to allow SC2City to access the MapAnalyzer API.
*
* @param AI --> The SC2City AI object.
*
* @param debug --> A setting to enable debugging features for functions.
*
"""


class MapAnalyzerInterface:
    # Constants:
    EXTRA_GROUND_DISTANCE: int = 3
    EXTRA_AIR_DISTANCE: int = 3

    # Initialization:
    def __init__(self, AI: BotAI = None, debug: bool = False) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

        # Objects:
        self.MapData: MapData = MapData(bot=AI, loglevel="INFO")

        # Booleans:
        self.debug: bool = debug

        # Grids:
        self.enemy_ground_to_air_grid: typing.Optional[numpy.ndarray] = None
        self.enemy_ground_grid: typing.Optional[numpy.ndarray] = None
        self.enemy_air_grid: typing.Optional[numpy.ndarray] = None

        self.reaper_grid: typing.Optional[numpy.ndarray] = None

    # Methods:

    """
    * A method to construct influential maps indicating the enemy's influence.
    *
    """

    def create_influence_maps(self) -> None:
        # Constructing Grids:
        self.enemy_ground_to_air_grid: numpy.ndarray = self.MapData.get_clean_air_grid(
            default_weight=1
        )
        self.enemy_ground_grid: numpy.ndarray = self.MapData.get_pyastar_grid(
            default_weight=1
        )
        self.enemy_air_grid: numpy.ndarray = self.MapData.get_pyastar_grid(
            default_weight=1
        )

        self.reaper_grid: numpy.ndarray = self.MapData.get_climber_grid(
            default_weight=1
        )

        for enemy_unit in self.AI.MemoryManager.enemy_unit_tag_to_unit_object.values():
            # Debugging:
            if self.debug:
                self.AI.client.debug_sphere_out(
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
                ) = self.MapData.add_cost_to_multiple_grids(
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
                    self.enemy_air_grid = self.MapData.add_cost(
                        position=enemy_unit.position,
                        radius=enemy_total_range,
                        grid=self.enemy_air_grid,
                        weight=enemy_unit.air_dps,
                    )
                else:
                    (
                        self.enemy_ground_to_air_grid,
                        self.enemy_air_grid,
                    ) = self.MapData.add_cost_to_multiple_grids(
                        position=enemy_unit.position,
                        radius=enemy_total_range,
                        grids=[self.enemy_ground_to_air_grid, self.enemy_air_grid],
                        weight=enemy_unit.air_dps,
                    )

                if self.debug:
                    # Variables:
                    color: Point3 = Point3((201, 168, 79))
                    size: int = 14

                    for x, y in zip(*numpy.where(self.enemy_ground_grid > 1)):
                        height: float = self.AI.get_terrain_z_height(
                            self.AI.start_location
                        )

                        position: Point3 = Point3((x, y, height))

                        if self.enemy_ground_grid[x, y] == numpy.inf:
                            continue

                        value: int = int(self.enemy_ground_grid[x, y])
                        self.AI.client.debug_text_world(
                            text=str(value), pos=position, color=color, size=size
                        )
