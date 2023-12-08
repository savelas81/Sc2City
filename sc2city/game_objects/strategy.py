from dataclasses import dataclass, field

from .order import Order
from .building_placements import BuildingPlacements
from .scout_time import ScoutTime

from utils import BuildTypes


@dataclass
class Strategy:
    build_type: BuildTypes = BuildTypes["ONE_BASE"]
    building_placements: BuildingPlacements = field(default_factory=BuildingPlacements)
    scout_times: list[ScoutTime] = field(default_factory=list)
    build_order: list[Order] = field(default_factory=list)

    @classmethod
    def from_dict(cls, dct: dict, map_file: str):
        return cls(
            build_type=BuildTypes[dct["build_type"]],
            building_placements=BuildingPlacements.from_build_type(
                BuildTypes[dct["build_type"]], map_file
            ),
            scout_times=[
                ScoutTime.from_dict(scout_time) for scout_time in dct["scout_times"]
            ],
            build_order=[Order.from_dict(order) for order in dct["build_order"]],
        )
