import enum
import json
import heapq
from dataclasses import dataclass, field
from collections import defaultdict

from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.bot_ai import BotAI

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


@dataclass
class BuildingPlacements:
    # TODO: Add a default building placements to fallback on
    lists: dict[PositionPriority, list[Point2]] = field(
        default_factory=lambda: defaultdict(list[Point2])
    )

    @classmethod
    def from_dict(cls, dct: dict):
        lists = {
            PositionPriority[key.upper()]: [Point2(coord) for coord in value]
            for key, value in dct.items()
        }
        return cls(lists)

    @classmethod
    def from_build_type(cls, build_type: BuildTypes, map_file: str):
        build_path = build_type.value
        file = build_path + map_file
        # TODO: Add a default building placements file to fallback on
        with open(file, "r") as f:
            building_placements = json.load(f)
        return cls.from_dict(building_placements)


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


MAP_PINS = {
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


# TODO: Move this to a map editor module
def save_map_pins(bot: BotAI) -> dict[PositionPriority, list[Point2]]:
    positions_dict = {key: [] for key in PositionPriority}

    for structure in bot.structures:
        if structure.type_id in MAP_PINS:
            priority, order = MAP_PINS[structure.type_id]
            positions_dict[priority].append((order, structure.position))

    for key in positions_dict:
        positions_dict[key] = [
            x[1] for x in heapq.nsmallest(len(positions_dict[key]), positions_dict[key])
        ]
    return positions_dict
