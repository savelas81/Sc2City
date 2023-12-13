import enum
from dataclasses import dataclass, field

from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2

from .building_placements import BuildingPlacements
from utils import BuildTypes, OrderType, Status


class CustomOrders(enum.Enum):
    WORKER_TO_MINS = 5000
    WORKER_TO_GAS = 5001
    WORKER_TO_GAS_3 = 5002
    WORKER_TO_SCOUT = 5003
    WORKER_FROM_SCOUT = 5004
    DO_NOTHING_1_SEC = 5005
    DO_NOTHING_5_SEC = 5006
    BARRACKS_DETACH_TECHLAB = 5007
    BARRACKS_DETACH_REACTOR = 5008
    BARRACKS_ATTACH_TECHLAB = 5009
    BARRACKS_ATTACH_REACTOR = 5010
    FACTORY_DETACH_TECHLAB = 5011
    FACTORY_DETACH_REACTOR = 5012
    FACTORY_ATTACH_TECHLAB = 5013
    FACTORY_ATTACH_REACTOR = 5014
    STARPORT_DETACH_TECHLAB = 5015
    STARPORT_DETACH_REACTOR = 5016
    STARPORT_ATTACH_TECHLAB = 5017
    STARPORT_ATTACH_REACTOR = 5018


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
    id: UnitTypeId | UpgradeId | AbilityId | CustomOrders
    priority: int = 0
    status: Status = Status.PENDING
    status_age: int = 0  # Measured in frames
    age: int = 0  # Measured in frames
    can_skip: bool = True
    tag: int = None
    target: Point2 | Unit = None
    quantity: int = 1
    comment: str = ""

    # Legacy properties
    conditional: bool = True
    conditional_behavior: str = "skip"  # TODO: Enumerate the possible values
    target_value_behavior: bool = False

    @classmethod
    def from_dict(cls, dct):
        dct["type"] = OrderType[dct["type"]]
        if dct["id"] in UnitTypeId.__members__:
            dct["id"] = UnitTypeId[dct["id"]]
        elif dct["id"] in UpgradeId.__members__:
            dct["id"] = UpgradeId[dct["id"]]
        elif dct["id"] in AbilityId.__members__:
            dct["id"] = AbilityId[dct["id"]]
        elif dct["id"] in CustomOrders.__members__:
            dct["id"] = CustomOrders[dct["id"]]
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
