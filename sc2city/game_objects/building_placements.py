import enum
import json
from typing import TypeAlias
from dataclasses import dataclass, field
from collections import defaultdict

from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId

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


PositionPriorityLists: TypeAlias = dict[PositionPriority, list[Point2]]


@dataclass
class BuildingPlacements:
    # TODO: Add a default building placements to fallback on
    _lists: PositionPriorityLists = field(
        default_factory=lambda: defaultdict(list[Point2])
    )

    @classmethod
    def from_dict(cls, dct: dict):
        _lists = {
            PositionPriority[key.upper()]: [Point2(coord) for coord in value]
            for key, value in dct.items()
        }
        return cls(_lists)

    @classmethod
    def from_build_type(cls, build_type: BuildTypes, map_file: str):
        build_path = build_type.value
        file = build_path + map_file
        # TODO: Add a default building placements file to fallback on
        with open(file, "r") as f:
            building_placements = json.load(f)
        return cls.from_dict(building_placements)

    @property
    def main(self) -> list[Point2]:
        """
        Returns the main list of building placements.
        """
        return self._lists[PositionPriority.MAIN]

    @property
    def auxiliary(self) -> list[Point2]:
        """
        Returns the auxiliary list of building placements.
        """
        return self._lists[PositionPriority.AUXILIARY]

    @property
    def supply_depot(self) -> list[Point2]:
        """
        Returns the supply depot list of building placements.
        """
        return self._lists[PositionPriority.SUPPLY_DEPOT]

    @property
    def turret(self) -> list[Point2]:
        """
        Returns the turret list of building placements.
        """
        return self._lists[PositionPriority.TURRET]

    @property
    def macro_orbital(self) -> list[Point2]:
        """
        Returns the macro orbital list of building placements.
        """
        return self._lists[PositionPriority.MACRO_ORBITAL]

    @property
    def expansion(self) -> list[Point2]:
        """
        Returns the expansion list of building placements.
        """
        return self._lists[PositionPriority.EXPANSION]

    @property
    def bunker(self) -> list[Point2]:
        """
        Returns the bunker list of building placements.
        """
        return self._lists[PositionPriority.BUNKER]

    @property
    def sensor_tower(self) -> list[Point2]:
        """
        Returns the sensor tower list of building placements.
        """
        return self._lists[PositionPriority.SENSOR_TOWER]

    def __getitem__(self, key: PositionPriority) -> list[Point2]:
        """
        Returns the list of building placements for the given priority.
        """
        return self._lists[key]

    def __setitem__(self, key: PositionPriority, value: list[Point2]) -> None:
        """
        Sets the list of building placements for the given priority.
        """
        self._lists[key] = value

    def __contains__(self, key: PositionPriority) -> bool:
        """
        Returns whether the given priority is in the building placements.
        """
        return key in self._lists

    def __iter__(self) -> PositionPriority:
        """
        Returns an iterator over the building placements.
        """
        return iter(self._lists)

    def __len__(self) -> int:
        """
        Returns the number of building placements.
        """
        return len(self._lists)


BUILDING_PRIORITY = {
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
