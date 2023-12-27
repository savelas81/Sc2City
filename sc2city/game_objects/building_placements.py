import enum
import json

from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2

from utils import BuildTypes


class PositionPriority(enum.Enum):
    MAIN = 0
    AUXILIARY = 1
    SUPPLY_DEPOT = 2
    TURRET = 3
    MACRO_ORBITAL = 4
    EXPANSION = 5
    BUNKER = 6
    SENSOR_TOWER = 7


BUILDING_PRIORITY: dict[UnitTypeId, PositionPriority] = {
    UnitTypeId.BARRACKS: PositionPriority.MAIN,
    UnitTypeId.FACTORY: PositionPriority.MAIN,
    UnitTypeId.STARPORT: PositionPriority.MAIN,
    UnitTypeId.ENGINEERINGBAY: PositionPriority.AUXILIARY,
    UnitTypeId.ARMORY: PositionPriority.AUXILIARY,
    UnitTypeId.GHOSTACADEMY: PositionPriority.AUXILIARY,
    UnitTypeId.FUSIONCORE: PositionPriority.AUXILIARY,
    UnitTypeId.MISSILETURRET: PositionPriority.TURRET,
    UnitTypeId.COMMANDCENTER: PositionPriority.EXPANSION,
    UnitTypeId.SUPPLYDEPOT: PositionPriority.SUPPLY_DEPOT,
    UnitTypeId.BUNKER: PositionPriority.BUNKER,
    UnitTypeId.SENSORTOWER: PositionPriority.SENSOR_TOWER,
}


MAP_PINS: dict[UnitTypeId, tuple[PositionPriority, int]] = {
    UnitTypeId.BARRACKS: (PositionPriority.MAIN, 1),
    UnitTypeId.FACTORY: (PositionPriority.MAIN, 2),
    UnitTypeId.STARPORT: (PositionPriority.MAIN, 3),
    UnitTypeId.GATEWAY: (PositionPriority.MAIN, 4),
    UnitTypeId.ROBOTICSFACILITY: (PositionPriority.MAIN, 5),
    UnitTypeId.ENGINEERINGBAY: (PositionPriority.AUXILIARY, 1),
    UnitTypeId.ARMORY: (PositionPriority.AUXILIARY, 2),
    UnitTypeId.GHOSTACADEMY: (PositionPriority.AUXILIARY, 3),
    UnitTypeId.SUPPLYDEPOTLOWERED: (PositionPriority.SUPPLY_DEPOT, 1),
    UnitTypeId.SUPPLYDEPOT: (PositionPriority.SUPPLY_DEPOT, 2),
    UnitTypeId.PYLON: (PositionPriority.SUPPLY_DEPOT, 3),
    UnitTypeId.TECHLAB: (PositionPriority.SUPPLY_DEPOT, 4),
    UnitTypeId.DARKSHRINE: (PositionPriority.SUPPLY_DEPOT, 5),
    UnitTypeId.MISSILETURRET: (PositionPriority.TURRET, 1),
    UnitTypeId.SPORECRAWLER: (PositionPriority.TURRET, 2),
    UnitTypeId.PHOTONCANNON: (PositionPriority.TURRET, 3),
    UnitTypeId.ORBITALCOMMAND: (PositionPriority.MACRO_ORBITAL, 1),
    UnitTypeId.NEXUS: (PositionPriority.EXPANSION, 1),
    UnitTypeId.PLANETARYFORTRESS: (PositionPriority.EXPANSION, 2),
    UnitTypeId.HATCHERY: (PositionPriority.EXPANSION, 3),
    UnitTypeId.BUNKER: (PositionPriority.BUNKER, 1),
    UnitTypeId.SENSORTOWER: (PositionPriority.SENSOR_TOWER, 1),
}


class BuildingPlacements(dict[PositionPriority, list[Point2]]):
    """
    A class representing the building placements in a Starcraft 2 map.

    This class extends the built-in `dict` class and maps `PositionPriority` to a list of `Point2` objects.
    It provides methods to initialize the building placements, load from a dictionary, and load from a build type.

    Attributes:
    - main (list[Point2]): The main list of building placements.
    - auxiliary (list[Point2]): The auxiliary list of building placements.
    - supply_depot (list[Point2]): The supply depot list of building placements.
    - turret (list[Point2]): The turret list of building placements.
    - macro_orbital (list[Point2]): The macro orbital list of building placements.
    - expansion (list[Point2]): The expansion list of building placements.
    - bunker (list[Point2]): The bunker list of building placements.
    - sensor_tower (list[Point2]): The sensor tower list of building placements.
    """

    # TODO: Add default building placements to fallback on if no build type is specified
    def __init__(self):
        super().__init__(
            {
                PositionPriority.MAIN: [],
                PositionPriority.AUXILIARY: [],
                PositionPriority.SUPPLY_DEPOT: [],
                PositionPriority.TURRET: [],
                PositionPriority.MACRO_ORBITAL: [],
                PositionPriority.EXPANSION: [],
                PositionPriority.BUNKER: [],
                PositionPriority.SENSOR_TOWER: [],
            }
        )

    @classmethod
    def from_dict(cls, dct: dict):
        """
        Creates a `BuildingPlacements` object from a dictionary.
        """
        new_instance = cls()
        for key, value in dct.items():
            if key.upper() in PositionPriority.__members__:
                new_instance[PositionPriority[key.upper()]] = [
                    Point2(coord) for coord in value
                ]
        return new_instance

    @classmethod
    def from_build_type(cls, build_type: BuildTypes, map_file: str):
        """
        Creates a `BuildingPlacements` object from a build type and map file.

        Args:
            build_type (BuildTypes): The build type.
            map_file (str): The path to the map file.

        Returns:
            BuildingPlacements: The `BuildingPlacements` object.
        """
        build_path = build_type.value
        file = build_path + map_file
        with open(file, "r") as f:
            building_placements = json.load(f)
        return cls.from_dict(building_placements)

    @property
    def main(self) -> list[Point2]:
        """
        Returns the main list of building placements.
        """
        return self[PositionPriority.MAIN]

    @property
    def auxiliary(self) -> list[Point2]:
        """
        Returns the auxiliary list of building placements.
        """
        return self[PositionPriority.AUXILIARY]

    @property
    def supply_depot(self) -> list[Point2]:
        """
        Returns the supply depot list of building placements.
        """
        return self[PositionPriority.SUPPLY_DEPOT]

    @property
    def turret(self) -> list[Point2]:
        """
        Returns the turret list of building placements.
        """
        return self[PositionPriority.TURRET]

    @property
    def macro_orbital(self) -> list[Point2]:
        """
        Returns the macro orbital list of building placements.
        """
        return self[PositionPriority.MACRO_ORBITAL]

    @property
    def expansion(self) -> list[Point2]:
        """
        Returns the expansion list of building placements.
        """
        return self[PositionPriority.EXPANSION]

    @property
    def bunker(self) -> list[Point2]:
        """
        Returns the bunker list of building placements.
        """
        return self[PositionPriority.BUNKER]

    @property
    def sensor_tower(self) -> list[Point2]:
        """
        Returns the sensor tower list of building placements.
        """
        return self[PositionPriority.SENSOR_TOWER]
