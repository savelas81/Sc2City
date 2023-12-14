import enum
from dataclasses import dataclass, field

from sc2.bot_ai import BotAI
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
        matching_type = next(
            (
                t
                for t in [UnitTypeId, UpgradeId, AbilityId, CustomOrders]
                if dct["id"] in t.__members__
            ),
            None,
        )
        if matching_type:
            dct["id"] = matching_type[dct["id"]]
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


class Base:
    """
    Represents a base in the game.

    Attributes:
    - location: The position of the base.
    - townhalls: A list of townhall tags associated with the base.
    - mineral_fields: A list of mineral field tags within range of the base.
    - vespene_geysers: A list of vespene geyser tags within range of the base.
    - mineral_workers: A list of worker tags assigned to mine minerals.
    - vespene_workers: A list of worker tags assigned to gather vespene gas.
    - structures: A list of structure tags associated with the base.

    Properties:
    - mineral_workers_needed: Total number of workers needed based on the number of mineral fields.
    - vespene_workers_needed: Total number of workers needed based on the number of vespene geysers.
    - mineral_workers_assigned: Number of workers assigned to minerals.
    - vespene_workers_assigned: Number of workers assigned to vespene.
    - mineral_workers_surplus: Number of extra workers assigned to minerals.
    - vespene_workers_surplus: Number of extra workers assigned to vespene.
    - mineral_workers_deficit: Number of workers that can still be assigned to minerals before saturation.
    - vespene_workers_deficit: Number of workers that can still be assigned to vespene before saturation.
    - mineral_workers_available: Number of workers above mineral saturation.
    - vespene_workers_available: Number of workers above vespene saturation.

    Methods:
    - add_townhall(townhall: Unit): Add a townhall to the base.
    - add_worker_to_minerals(worker: Unit): Add a worker to the mineral workers list.
    - add_worker_to_vespene(worker: Unit): Add a worker to the vespene workers list.
    - add_structure(structure: Unit): Add a structure to the structures list.
    - remove_worker_from_minerals(worker: Unit): Remove a worker from the mineral workers list.
    - remove_worker_from_vespene(worker: Unit): Remove a worker from the vespene workers list.
    - remove_structure(structure: Unit): Remove a structure from the structures list.
    - remove_mineral_field(mineral_field: Unit): Remove a mineral field from the mineral fields list.
    - remove_vespene_geyser(vespene_geyser: Unit): Remove a vespene geyser from the vespene geysers list.
    - remove_townhall(townhall: Unit): Remove a townhall from the townhalls list.
    """

    def __init__(self, bot: BotAI, townhall: Unit):
        self.location = townhall.position
        self.townhalls = [townhall.tag]
        self.mineral_fields = bot.mineral_field.closer_than(10, townhall).tags
        self.vespene_geysers = bot.vespene_geyser.closer_than(10, townhall).tags
        self.mineral_workers = []
        self.vespene_workers = []
        self.structures = []

    @property
    def mineral_workers_needed(self) -> int:
        """
        Total number of workers needed based on the number of mineral fields.
        """
        return len(self.mineral_fields) * 2

    @property
    def vespene_workers_needed(self) -> int:
        """
        Total number of workers needed based on the number of vespene geysers.
        """
        return len(self.vespene_geysers) * 3

    @property
    def mineral_workers_assigned(self) -> int:
        """
        Number of workers assigned to minerals.
        """
        return len(self.mineral_workers)

    @property
    def vespene_workers_assigned(self) -> int:
        """
        Number of workers assigned to vespene.
        """
        return len(self.vespene_workers)

    @property
    def mineral_workers_surplus(self) -> int:
        """
        Number of extra workers assigned to minerals.
        """
        return self.mineral_workers_assigned - self.mineral_workers_needed

    @property
    def vespene_workers_surplus(self) -> int:
        """
        Number of extra workers assigned to vespene.
        """
        return self.vespene_workers_assigned - self.vespene_workers_needed

    @property
    def mineral_workers_deficit(self) -> int:
        """
        Number of workers that can still be assigned to minerals before saturation.
        """
        return self.mineral_workers_needed - self.mineral_workers_assigned

    @property
    def vespene_workers_deficit(self) -> int:
        """
        Number of workers that can still be assigned to vespene before saturation.
        """
        return self.vespene_workers_needed - self.vespene_workers_assigned

    @property
    def mineral_workers_available(self) -> int:
        """
        Number of workers above mineral saturation.
        """
        return self.mineral_workers_surplus > 0

    @property
    def vespene_workers_available(self) -> int:
        """
        Number of workers above vespene saturation.
        """
        return self.vespene_workers_surplus > 0

    def add_townhall(self, townhall: Unit) -> None:
        """
        Add a townhall to the base.
        """
        self.townhalls.append(townhall.tag)

    def add_worker_to_minerals(self, worker: Unit) -> None:
        """
        Add a worker to the mineral workers list.
        """
        self.mineral_workers.append(worker.tag)

    def add_worker_to_vespene(self, worker: Unit) -> None:
        """
        Add a worker to the vespene workers list.
        """
        self.vespene_workers.append(worker.tag)

    def add_structure(self, structure: Unit) -> None:
        """
        Add a structure to the structures list.
        """
        self.structures.append(structure.tag)

    def remove_worker_from_minerals(self, worker: Unit) -> None:
        """
        Remove a worker from the mineral workers list.
        """
        self.mineral_workers.remove(worker.tag)

    def remove_worker_from_vespene(self, worker: Unit) -> None:
        """
        Remove a worker from the vespene workers list.
        """
        self.vespene_workers.remove(worker.tag)

    def remove_structure(self, structure: Unit) -> None:
        """
        Remove a structure from the structures list.
        """
        self.structures.remove(structure.tag)

    def remove_mineral_field(self, mineral_field: Unit) -> None:
        """
        Remove a mineral field from the mineral fields list.
        """
        self.mineral_fields.remove(mineral_field.tag)

    def remove_vespene_geyser(self, vespene_geyser: Unit) -> None:
        """
        Remove a vespene geyser from the vespene geysers list.
        """
        self.vespene_geysers.remove(vespene_geyser.tag)

    def remove_townhall(self, townhall: Unit) -> None:
        """
        Remove a townhall from the townhalls list.
        """
        self.townhalls.remove(townhall.tag)
