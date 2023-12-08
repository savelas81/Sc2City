from dataclasses import dataclass, field

from sc2.ids.unit_typeid import UnitTypeId

from .order import Order
from .building_placements import BuildingPlacements
from .scout_time import ScoutTime

from utils import BuildTypes, OrderType, Status


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


@dataclass
class ScoutTime:
    id: UnitTypeId = UnitTypeId.SCV
    time: int = 37
    comment: str = ""

    @classmethod
    def from_dict(cls, dct):
        dct["id"] = UnitTypeId[dct["id"]]
        return cls(**dct)


@dataclass
class Order:
    type: OrderType
    id: UnitTypeId
    priority: int = 0
    target_value: int = 1
    conditional: bool = True
    conditional_behavior: str = "skip"  # TODO: Enumerate the possible values
    target_value_behavior: bool = False
    status: Status = Status.PENDING
    comment: str = ""

    @classmethod
    def from_dict(cls, dct):
        dct["type"] = OrderType[dct["type"]]
        dct["id"] = UnitTypeId[dct["id"]]
        return cls(**dct)
