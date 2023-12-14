import enum
from dataclasses import dataclass, field

from sc2.bot_ai import BotAI
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2

from .building_placements import BuildingPlacements
from utils import BuildTypes, OrderType, Status, SCVAssignment


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
    build_order: list[Order] = field(default_factory=list)

    @classmethod
    def from_dict(cls, dct: dict, map_file: str):
        return cls(
            build_type=BuildTypes[dct["build_type"]],
            building_placements=BuildingPlacements.from_build_type(
                BuildTypes[dct["build_type"]], map_file
            ),
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


class Workers(dict[SCVAssignment, dict[int, int] | set[int]]):
    """
    Represents a collection of workers in the game.

    This class extends the built-in `dict` class and provides additional properties and methods
    for managing workers and their assignments.

    Attributes:
        mineral_miners (dict[int, int]): A dictionary mapping worker tags to mineral resource tags.
        vespene_miners (dict[int, int]): A dictionary mapping worker tags to vespene resource tags.
        builders (set[int]): A set of worker tags assigned to building tasks.
        scouts (set[int]): A set of worker tags assigned to scouting tasks.
        repairers (set[int]): A set of worker tags assigned to repair tasks.
        army (set[int]): A set of worker tags assigned to army tasks.
        none (set[int]): A set of worker tags with no assigned task.
        all (set[int]): A set of all worker tags.
        mineral_tags (set[int]): A set of all mineral resource tags.
        vespene_tags (set[int]): A set of all vespene resource tags.

    Methods:
        remove(worker: Unit | int, assignment: SCVAssignment = None): Removes the given worker from the given assignment.
        add(worker: Unit | int, assignment: SCVAssignment, resource: Unit | int = None): Adds the given worker to the given assignment.
        get_assignment(worker: Unit | int): Returns the current assignment of a worker.
        change_assignment(worker: Unit | int, new_assignment: SCVAssignment, resource: Unit | int = None, is_new: bool = False, old_assignment: SCVAssignment = None): Change the assignment of a worker to a new assignment.
        get_resource_tag(worker: Unit | int, assignment: SCVAssignment = None): Get the resource tag (mineral or vespene) assigned to the worker.
    """

    def __init__(self):
        super().__init__(
            {
                SCVAssignment.MINERALS: dict[int, int](),
                SCVAssignment.VESPENE: dict[int, int](),
                SCVAssignment.BUILD: set[int](),
                SCVAssignment.SCOUT: set[int](),
                SCVAssignment.REPAIR: set[int](),
                SCVAssignment.ARMY: set[int](),
                SCVAssignment.NONE: set[int](),
            }
        )

    @property
    def mineral_miners(self) -> dict[int, int]:
        """
        Returns the mineral workers dictionary.
        """
        return self[SCVAssignment.MINERALS]

    @property
    def gas_miners(self) -> dict[int, int]:
        """
        Returns the vespene workers dictionary.
        """
        return self[SCVAssignment.VESPENE]

    @property
    def builders(self) -> set[int]:
        """
        Returns the build workers set.
        """
        return self[SCVAssignment.BUILD]

    @property
    def scouts(self) -> set[int]:
        """
        Returns the scout workers set.
        """
        return self[SCVAssignment.SCOUT]

    @property
    def repairers(self) -> set[int]:
        """
        Returns the repair workers set.
        """
        return self[SCVAssignment.REPAIR]

    @property
    def army(self) -> set[int]:
        """
        Returns the army workers set.
        """
        return self[SCVAssignment.ARMY]

    @property
    def none(self) -> set[int]:
        """
        Returns the none workers set.
        """
        return self[SCVAssignment.NONE]

    @property
    def all(self) -> set[int]:
        """
        Returns all workers.
        """
        return (
            self[SCVAssignment.MINERALS].keys()
            | self[SCVAssignment.VESPENE].keys()
            | self[SCVAssignment.BUILD]
            | self[SCVAssignment.SCOUT]
            | self[SCVAssignment.REPAIR]
            | self[SCVAssignment.ARMY]
            | self[SCVAssignment.NONE]
        )

    @property
    def mineral_tags(self) -> set[int]:
        """
        Returns all mineral worker tags.
        """
        return self[SCVAssignment.MINERALS].values()

    @property
    def vespene_tags(self) -> set[int]:
        """
        Returns all vespene worker tags.
        """
        return self[SCVAssignment.VESPENE].values()

    def remove(self, worker: Unit | int, assignment: SCVAssignment = None) -> None:
        """
        Removes the given worker from the given assignment.

        If the assignment is not provided, it will try to find it.
        """
        if not assignment:
            assignment = self.get_assignment(worker)

        if not assignment:
            return

        worker_tag = self.__get_tag(worker)
        if assignment in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            del self[assignment][worker_tag]
        else:
            self[assignment].remove(worker_tag)

    def add(
        self, worker: Unit | int, assignment: SCVAssignment, resource: Unit | int = None
    ) -> None:
        """
        Adds the given worker to the given assignment.

        If the assignment involves a resource, the resource must be provided.
        """
        worker_tag = self.__get_tag(worker)
        if assignment in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            if not resource:
                raise ValueError(
                    f"Resource not provided for worker {worker_tag} and assignment {assignment}"
                )
            resource_tag = self.__get_tag(resource)
            self[assignment][worker_tag] = resource_tag
        else:
            self[assignment].add(worker_tag)

    def get_assignment(self, worker: Unit | int) -> SCVAssignment | None:
        """
        Returns the current assignment of a worker.
        """
        worker_tag = self.__get_tag(worker)
        return next(
            (
                assignment
                for assignment, workers in self.items()
                if worker_tag in workers
            ),
            None,
        )

    def change_assignment(
        self,
        worker: Unit | int,
        new_assignment: SCVAssignment,
        resource: Unit | int = None,
        is_new: bool = False,
        old_assignment: SCVAssignment = None,
    ) -> None:
        """
        Change the assignment of a worker to a new assignment.

        Args:
            worker (Unit | int): The worker unit or worker ID.
            new_assignment (SCVAssignment): The new assignment for the worker.
            resource (Unit | int, optional): If the assignment involves a resource,
                the resource must be provided.
            is_new (bool, optional): Indicates if the worker is new. Set to true to skip
                trying to find the old assignment. Defaults to False.
            old_assignment (SCVAssignment, optional): The old assignment of the worker.
                If the assignment is not provided, it will try to find it.
        """
        if not is_new:
            self.remove(worker, old_assignment)
        self.add(worker, new_assignment, resource)

    def get_resource_tag(
        self,
        worker: Unit | int,
        assignment: SCVAssignment = None,
    ) -> int | None:
        """
        Get the resource tag (mineral or vespene) assigned to the worker.

        Args:
            worker (Unit): The worker unit.
            assignment (SCVAssignment, optional): The assignment of the worker. If not provided it will try to find.
            return_tag (bool, optional): Whether to return the resource tag instead of the unit. Defaults to False.

        Returns:
            Unit | int | None: The resource unit or its tag, or None if the assignment is invalid.
        """
        if not assignment:
            assignment = self.get_assignment(worker)

        if assignment not in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            return None

        worker_tag = self.__get_tag(worker)
        return self[assignment][worker_tag]

    def __get_tag(self, unit: Unit | int) -> int:
        """
        Returns the tag of the given unit.
        """
        return unit.tag if isinstance(unit, Unit) else unit
