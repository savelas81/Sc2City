from dataclasses import dataclass, field

from sc2.ids.unit_typeid import UnitTypeId

from .building_placements import BuildingPlacements
from utils import BuildTypes, OrderType, Status


@dataclass
class ScoutTime:
    id: UnitTypeId = UnitTypeId.SCV
    time: int = 37
    comment: str = ""

    @classmethod
    def from_dict(cls, dct):
        dct["id"] = UnitTypeId[dct["id"]]
        return cls(**dct)


# TODO: Add conditional behavior
@dataclass
class Order:
    type: OrderType
    id: UnitTypeId
    priority: int = 0
    status: Status = Status.PENDING
    status_age: int = 0  # Measured in frames
    age: int = 0  # Measured in frames
    worker_tag: int = None
    can_skip: bool = True
    conditional: bool = True
    conditional_behavior: str = "skip"  # TODO: Enumerate the possible values
    target_value_behavior: bool = False
    target_value: int = 1
    comment: str = ""

    @classmethod
    def from_dict(cls, dct):
        dct["type"] = OrderType[dct["type"]]
        dct["id"] = UnitTypeId[dct["id"]]
        return cls(**dct)

    def update_status(self, new_status: Status) -> None:
        if new_status != self.status:
            self.status = new_status
            self.status_age = 0  # Reset the status age

    def get_old(self, game_step: int) -> None:
        self.status_age += game_step
        self.age += game_step

    def reset_ages(self) -> None:
        self.status_age = 0
        self.age = 0


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
