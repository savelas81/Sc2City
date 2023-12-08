import json
from dataclasses import dataclass, field

from sc2.position import Point2

from utils import BuildTypes


# Why have more than one list for each category?
@dataclass
class BuildingPlacements:
    # TODO: Add a default building placements to fallback on
    building_positions_priority_1: list[Point2] = field(default_factory=list)
    building_positions_priority_2: list[Point2] = field(default_factory=list)
    building_positions_priority_3: list[Point2] = field(default_factory=list)
    building_positions_priority_4: list[Point2] = field(default_factory=list)
    building_positions_priority_5: list[Point2] = field(default_factory=list)
    auxiliary_buildings_1: list[Point2] = field(default_factory=list)
    auxiliary_buildings_2: list[Point2] = field(default_factory=list)
    auxiliary_buildings_3: list[Point2] = field(default_factory=list)
    supply_depot_positions_priority_1: list[Point2] = field(default_factory=list)
    supply_depot_positions_priority_2: list[Point2] = field(default_factory=list)
    supply_depot_positions_priority_3: list[Point2] = field(default_factory=list)
    supply_depot_positions_priority_4: list[Point2] = field(default_factory=list)
    supply_depot_positions_priority_5: list[Point2] = field(default_factory=list)
    turret_positions_priority_1: list[Point2] = field(default_factory=list)
    turret_positions_priority_2: list[Point2] = field(default_factory=list)
    turret_positions_priority_3: list[Point2] = field(default_factory=list)
    macro_orbitals: list[Point2] = field(default_factory=list)
    expansion_priority_1: list[Point2] = field(default_factory=list)
    expansion_priority_2: list[Point2] = field(default_factory=list)
    expansion_priority_3: list[Point2] = field(default_factory=list)
    bunkers: list[Point2] = field(default_factory=list)
    sensor_towers: list[Point2] = field(default_factory=list)

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(**dct)

    @classmethod
    def from_build_type(cls, build_type: BuildTypes, map_file: str):
        build_path = build_type.value
        file = build_path + map_file
        # TODO: Add a default building placements file to fallback on
        with open(file, "r") as f:
            building_placements = json.load(f)
        return cls.from_dict(building_placements)
