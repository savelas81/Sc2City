# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# MapAnalyzer:
# > MapData:
from MapAnalyzer.MapData import MapData

# StarCraft II:
# > Position:
from sc2.position import Point3

# Numpy:
import numpy as np


# Classes:

""""""

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
    def create_influence_maps(self, memory) -> None:
        self.enemy_ground_to_air_grid: np.ndarry = self.map_data.get_clean_air_grid(default_weight=1)
        self.enemy_ground_grid: np.ndarray = self.map_data.get_pyastar_grid(default_weight=1)
        self.enemy_air_grid: np.ndarry = self.map_data.get_clean_air_grid(default_weight=1)

        self.reaper_grid: np.ndarray = self.map_data.get_climber_grid(default_weight=1)
        extra_ground_distance = 3
        extra_air_distance = 3
        for enemy_unit in memory.enemy_units_in_memory:
            self.ai.client.debug_sphere_out(
                p=enemy_unit, r=enemy_unit.radius, color=(255, 0, 0)
            )
            if enemy_unit.can_attack_ground:
                enemy_total_range = (
                    enemy_unit.radius + enemy_unit.ground_range + extra_ground_distance
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
            if enemy_unit.can_attack_air:
                enemy_total_range = (
                    enemy_unit.radius + enemy_unit.air_range + extra_air_distance
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
        if self.debug:
            color = Point3((201, 168, 79))
            size: int = 14
            for x, y in zip(*np.where(self.enemy_ground_grid > 1)):
                height: float = self.ai.get_terrain_z_height(self.ai.start_location)
                pos: Point3 = Point3((x, y, height))
                if self.enemy_ground_grid[x, y] == np.inf:
                    continue
                else:
                    val: int = int(self.enemy_ground_grid[x, y])
                self.ai.client.debug_text_world(str(val), pos, color, size)
