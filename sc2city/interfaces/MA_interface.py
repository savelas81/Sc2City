# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > Position:
from sc2.position import Point3

# MapAnalyzer:
# > MapData:
from sc2city.MapAnalyzer.MapData import MapData

# Numpy:
import numpy as np

# Managers:
from sc2city.managers import MemoryManager

# Classes:

"""
TODO: Add documentation here..
"""

class MapAnalyserInterface:
    # Initialization:
    def __init__(self, AI: BotAI = None) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI
        self.MapData: MapData = MapData(AI, loglevel="INFO")

        # Booleans:
        self.debug: bool = True

        # Grids:
        self.enemy_ground_to_air_grid = None
        self.enemy_ground_grid = None
        self.enemy_air_grid = None
        self.reaper_grid = None

    # Methods:
    def create_influence_maps(self, memory: MemoryManager) -> None:
        self.enemy_ground_to_air_grid: np.ndarray = self.MapData.get_clean_air_grid(default_weight=1)
        self.enemy_ground_grid: np.ndarray = self.MapData.get_pyastar_grid(default_weight=1)
        self.enemy_air_grid: np.ndarray = self.MapData.get_clean_air_grid(default_weight=1)

        self.reaper_grid: np.ndarray = self.MapData.get_climber_grid(default_weight=1)
        extra_ground_distance = 3
        extra_air_distance = 3
        for enemy_unit in memory.enemy_unit_tag_to_unit_object.values():
            self.AI.client.debug_sphere_out(
                p=enemy_unit, r=enemy_unit.radius, color=(255, 0, 0)
            )
            if enemy_unit.can_attack_ground:
                enemy_total_range = (
                    enemy_unit.radius + enemy_unit.ground_range + extra_ground_distance
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
            if enemy_unit.can_attack_air:
                enemy_total_range = (
                    enemy_unit.radius + enemy_unit.air_range + extra_air_distance
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
            color = Point3((201, 168, 79))
            size: int = 14
            for x, y in zip(*np.where(self.enemy_ground_grid > 1)):
                height: float = self.AI.get_terrain_z_height(self.AI.start_location)
                pos: Point3 = Point3((x, y, height))
                if self.enemy_ground_grid[x, y] == np.inf:
                    continue
                else:
                    val: int = int(self.enemy_ground_grid[x, y])
                self.AI.client.debug_text_world(str(val), pos, color, size)
