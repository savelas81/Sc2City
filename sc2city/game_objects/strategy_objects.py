import enum
import functools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

import numpy as np
from sc2.bot_ai import BotAI
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units
from sklearn.linear_model import LinearRegression

from utils import BuildTypes, OrderType, SCVAssignment, Status

from .building_placements import BuildingPlacements

if TYPE_CHECKING:
    from Sc2City import Sc2City


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
    """
    ### Production orders to be executed.

    ### Attributes:
    - type (OrderType): The type of order.
    - id (UnitTypeId | UpgradeId | AbilityId | CustomOrders): The id of the unit, upgrade or ability.
    - priority (int): The priority of the order.
    - status (Status): The status of the order.
    - status_age (int): The number of frames since the status was last updated.
    - age (int): The number of frames since the order was created.
    - can_skip (bool): Indicates if the order can be skipped.
    - tag (int): The tag of the unit that is executing the order.
    - target (Point2 | Unit): The target of the order.
    - quantity (int): The quantity of the order.
    - comment (str): A comment for the order.

    ### Methods:
    - from_dict(dct: dict) -> Order: Creates an order from a dictionary.
    - update_status(new_status: Status) -> None: Updates the status of the order.
    - get_old(game_step: int) -> None: Increases the status age and the age of the order.
    - reset_ages() -> None: Resets the status age and the age of the order.
    """

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
        """
        Creates an order from a dictionary.
        """
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
        """
        Updates the status of the order.
        """
        if new_status != self.status:
            self.status = new_status
            self.status_age = 0  # Reset the status age

    def get_old(self, game_step: int) -> None:
        """
        Increases the status age and the age of the order.
        """
        self.status_age += game_step
        self.age += game_step

    def reset_ages(self) -> None:
        """
        Resets the status age and the age of the order.
        """
        self.status_age = 0
        self.age = 0


@dataclass
class Strategy:
    """
    ### The strategy to be executed.

    ### Attributes:
    - build_type (BuildTypes): The type of build to be executed.
    - building_placements (BuildingPlacements): All possible building placements for the strategy.
    - build_order (list[Order]): The build order for the strategy.

    ### Methods:
    - from_dict(dct: dict, map_file: str) -> Strategy: Creates a strategy from a dictionary.
    """

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


def get_tags(func):
    """
    Decorator to convert Unit objects to tags.
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        args = tuple(arg.tag if isinstance(arg, Unit) else arg for arg in args)
        return func(self, *args, **kwargs)

    return wrapper


def get_positions(func):
    """
    Decorator to convert Unit objects to positions.
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        args = tuple(arg.position if isinstance(arg, Unit) else arg for arg in args)
        return func(self, *args, **kwargs)

    return wrapper


class Base:
    """
    ### Represents a base in the game.

    ### Attributes:
    - bot (BotAI): The bot state.
    - location (Point2): The position of the base.
    - townhalls (set[int]): The set of townhall tags in the base.
    - mineral_workers (set[int]): The set of worker tags assigned to minerals in the base.
    - vespene_workers (set[int]): The set of worker tags assigned to vespene in the base.
    - structures (set[int]): The set of structure tags in the base.
    - enemy (bool): Indicates if the base belongs to the enemy.

    ### Properties:
    - mineral_fields (Units): The mineral fields belonging to this base.
    - vespene_geysers (Units): The vespene geysers belonging to this base.
    - refineries (Units): The refineries belonging to this base.
    - mineral_workers_needed (int): Total number of workers needed based on the number of mineral fields.
    - vespene_workers_needed (int): Total number of workers needed based on the number of vespene geysers.
    - mineral_workers_assigned (int): Number of workers assigned to minerals.
    - vespene_workers_assigned (int): Number of workers assigned to vespene.
    - mineral_workers_surplus (int): Number of extra workers assigned to minerals.
    - vespene_workers_surplus (int): Number of extra workers assigned to vespene.
    - mineral_workers_deficit (int): Number of workers that can still be assigned to minerals before saturation.
    - vespene_workers_deficit (int): Number of workers that can still be assigned to vespene before saturation.
    - mineral_workers_available (bool): If base has mineral workers above saturation.
    - vespene_workers_available (bool): If base has vespene workers above saturation.
    - workers_available (bool): If base has workers above saturation.
    - minerals_left (int): Number of minerals left in the base.
    - vespene_left (int): Number of vespene left in the base.
    - has_minerals (bool): If the base still has mineral fields.
    - has_vespene (bool): If the base still has vespene geysers.

    ### Methods:
    - add_townhall(townhall: Unit | int) -> None: Add a townhall to the base.
    - add_worker_to_minerals(worker: Unit | int) -> None: Add a worker to the mineral workers list.
    - add_worker_to_vespene(worker: Unit | int) -> None: Add a worker to the vespene workers list.
    - add_structure(structure: Unit | int) -> None: Add a structure to the structures list.
    - remove_worker_from_minerals(worker: Unit | int) -> None: Remove a worker from the mineral workers list.
    - remove_worker_from_vespene(worker: Unit | int) -> None: Remove a worker from the vespene workers list.
    - remove_structure(structure: Unit | int) -> None: Remove a structure from the structures list.
    - remove_mineral_field(mineral_field: Unit | int) -> None: Remove a mineral field from the mineral fields list.
    - remove_vespene_geyser(vespene_geyser: Unit | int) -> None: Remove a vespene geyser from the vespene geysers list.
    - remove_townhall(townhall: Unit | int) -> None: Remove a townhall from the townhalls list.
    """

    def __init__(self, bot: BotAI, position: Point2):
        self.__bot = bot
        self.location = position
        self.townhalls: set[int] = set()
        self.mineral_workers: set[int] = set()
        self.vespene_workers: set[int] = set()
        self.structures: set[int] = set()
        self.enemy = False

    @property
    def mineral_fields(self) -> Units:
        """
        The mineral fields belonging to this base.
        """
        return self.__bot.mineral_field.closer_than(10, self.location)

    @property
    def vespene_geysers(self) -> Units:
        """
        The vespene geysers belonging to this base.
        """
        return self.__bot.vespene_geyser.closer_than(10, self.location)

    @property
    def refineries(self) -> Units:
        """
        The refineries belonging to this base.
        """
        return self.__bot.gas_buildings.closer_than(10, self.location)

    @property
    def mineral_workers_needed(self) -> int:
        """
        Total number of workers needed based on the number of mineral fields.
        """
        return self.mineral_fields.amount * 2

    @property
    def vespene_workers_needed(self) -> int:
        """
        Total number of workers needed based on the number of vespene geysers.
        """
        return self.refineries.ready.filter(lambda r: r.has_vespene).amount * 3

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
        return max(0, self.mineral_workers_assigned - self.mineral_workers_needed)

    @property
    def vespene_workers_surplus(self) -> int:
        """
        Number of extra workers assigned to vespene.
        """
        return max(0, self.vespene_workers_assigned - self.vespene_workers_needed)

    @property
    def mineral_workers_deficit(self) -> int:
        """
        Number of workers that can still be assigned to minerals before saturation.
        """
        return max(0, self.mineral_workers_needed - self.mineral_workers_assigned)

    @property
    def vespene_workers_deficit(self) -> int:
        """
        Number of workers that can still be assigned to vespene before saturation.
        """
        return max(0, self.vespene_workers_needed - self.vespene_workers_assigned)

    @property
    def mineral_workers_available(self) -> bool:
        """
        If base has mineral workers above saturation.
        """
        return self.mineral_workers_surplus > 0

    @property
    def vespene_workers_available(self) -> bool:
        """
        If base has vespene workers above saturation.
        """
        return self.vespene_workers_surplus > 0

    @property
    def workers_available(self) -> bool:
        """
        If base has workers above saturation.
        """
        return self.mineral_workers_available or self.vespene_workers_available

    @property
    def minerals_left(self) -> int:
        """
        Number of minerals left in the base.
        """
        return sum(
            (mineral_field.mineral_contents for mineral_field in self.mineral_fields)
        )

    @property
    def vespene_left(self) -> int:
        """
        Number of vespene left in the base.
        """
        return sum(
            (vespene_geyser.vespene_contents for vespene_geyser in self.vespene_geysers)
        )

    @property
    def has_minerals(self) -> bool:
        """
        Indicates if the base still has mineral fields.
        """
        return bool(self.mineral_fields)

    @property
    def has_vespene(self) -> bool:
        """
        Indicates if the base still has vespene geysers.
        """
        return self.vespene_left > 0

    @get_tags
    def add_townhall(self, townhall: Unit | int) -> None:
        """
        Add a townhall to the base.
        """
        self.townhalls.add(townhall)

    @get_tags
    def add_worker_to_minerals(self, worker: Unit | int) -> None:
        """
        Add a worker to the mineral workers list.
        """
        self.mineral_workers.add(worker)

    @get_tags
    def add_worker_to_vespene(self, worker: Unit | int) -> None:
        """
        Add a worker to the vespene workers list.
        """
        self.vespene_workers.add(worker)

    @get_tags
    def add_structure(self, structure: Unit | int) -> None:
        """
        Add a structure to the structures list.
        """
        self.structures.add(structure)

    @get_tags
    def remove_worker_from_minerals(self, worker: Unit | int) -> None:
        """
        Remove a worker from the mineral workers list.
        """
        self.mineral_workers.remove(worker)

    @get_tags
    def remove_worker_from_vespene(self, worker: Unit | int) -> None:
        """
        Remove a worker from the vespene workers list.
        """
        self.vespene_workers.remove(worker)

    @get_tags
    def remove_structure(self, structure: Unit | int) -> None:
        """
        Remove a structure from the structures list.
        """
        self.structures.remove(structure)

    @get_tags
    def remove_townhall(self, townhall: Unit | int) -> None:
        """
        Remove a townhall from the townhalls list.
        """
        self.townhalls.remove(townhall)


class Bases(dict[Point2, Base]):
    """
    ### A collection of bases in the game.

    This class represents a dictionary of bases, where the keys are the locations of the bases and the values are instances of the Base class.
    Bases can be accessed using square bracket notation, e.g., bases[location].

    ### Attributes:
    - bot (BotAI): The bot instance associated with the bases.

    ### Properties:
    - owned: Returns bases that are owned by the bot.
    - enemy: Returns bases that are owned by the enemy.
    - empty: Returns bases that are empty.
    - first: Returns the first base.
    - last: Returns the last base.
    - random: Returns a random base.
    - have_minerals: Returns bases that still have mineral fields.
    - have_vespene: Returns bases that still have vespene geysers.
    - mineral_workers_needed: Returns the number of mineral workers needed to saturate all bases.
    - vespene_workers_needed: Returns the number of vespene workers needed to saturate all bases.
    - mineral_workers_assigned: Returns the number of workers assigned to minerals.
    - vespene_workers_assigned: Returns the number of workers assigned to vespene.
    - mineral_workers_surplus: Returns the number of extra workers assigned to minerals.
    - vespene_workers_surplus: Returns the number of extra workers assigned to vespene.
    - mineral_workers_deficit: Returns the number of workers that can still be assigned to minerals before saturation.
    - vespene_workers_deficit: Returns the number of workers that can still be assigned to vespene before saturation.
    - with_available_workers: Returns bases that have workers above saturation.
    - minerals_left: Returns the number of minerals left in all bases.
    - vespene_left: Returns the number of vespene left in all bases.

    ### Methods:
    - add(location: Point2 | list[Point2]) -> None: Add a new base location to the collection.
    - filter(condition: Callable[[Base], bool]) -> Bases: Returns bases that satisfy a given condition.
    - sorted(condition: Callable[[Base], bool]) -> list[Base]: Returns a list of bases sorted by a given condition.
    - closest_to(location: Unit | Point2) -> Base: Returns the base closest to the given location.
    - contains_worker(worker: Unit | int) -> Base | None: Returns the base that contains the given worker.
    - contains_resource(resource: Unit | int) -> Base | None: Returns the base that contains the given resource.
    - contains_structure(structure: Unit | int) -> Base | None: Returns the base that contains the given structure.
    - contains_townhall(townhall: Unit | int) -> Base | None: Returns the base that contains the given townhall.
    - remove_worker(worker: Unit | int) -> None: Removes the given worker from the base it is assigned to.
    - remove_structure(structure: Unit | int) -> None: Removes the given structure from the base it is assigned to.
    - remove_townhall(townhall: Unit | int) -> None: Removes the given townhall from the base it is assigned to.
    - remove_building(building: Unit | int) -> None: Removes the given building from the base it is assigned to.
    - assign_worker_to_resource(worker: Unit | int, resource: Unit | int) -> None: Assigns the given worker to the given resource.
    """

    def __init__(self, bot: BotAI):
        self.__bot = bot
        super().__init__()

    @property
    def owned(self) -> "Bases":
        """
        Returns bases that are owned by the bot.
        """
        return self.filter(lambda base: base.townhalls)

    @property
    def enemy(self) -> "Bases":
        """
        Returns base that are owned by the enemy.
        """
        return self.filter(lambda base: base.enemy)

    @property
    def empty(self) -> "Bases":
        """
        Returns the bases that are empty.
        """
        return self.filter(lambda base: not base.townhalls and not base.enemy)

    @property
    def first(self) -> Base:
        """
        Returns the first base.
        """
        return next(iter(self.values()), None)

    @property
    def last(self) -> Base:
        """
        Returns the last base.
        """
        return next(reversed(self.values()), None)

    @property
    def random(self) -> Base:
        """
        Returns a random base.
        """
        return np.random.choice(tuple(self.values()))

    @property
    def have_minerals(self) -> "Bases":
        """
        Returns the bases that still have mineral_fields.
        """
        return self.filter(lambda base: base.has_minerals)

    @property
    def have_vespene(self) -> "Bases":
        """
        Returns the bases that still have vespene_geysers.
        """
        return self.filter(lambda base: base.has_vespene)

    @property
    def mineral_workers_needed(self) -> int:
        """
        Returns the number of mineral workers needed to saturate all bases.
        """
        return sum(base.mineral_workers_needed for base in self.values())

    @property
    def vespene_workers_needed(self) -> int:
        """
        Returns the number of vespene workers needed to saturate all bases.
        """
        return sum(base.vespene_workers_needed for base in self.values())

    @property
    def mineral_workers_assigned(self) -> int:
        """
        Returns the number of workers assigned to minerals.
        """
        return sum(base.mineral_workers_assigned for base in self.values())

    @property
    def vespene_workers_assigned(self) -> int:
        """
        Returns the number of workers assigned to vespene.
        """
        return sum(base.vespene_workers_assigned for base in self.values())

    @property
    def mineral_workers_surplus(self) -> int:
        """
        Returns the number of extra workers assigned to minerals.
        """
        return sum(base.mineral_workers_surplus for base in self.values())

    @property
    def vespene_workers_surplus(self) -> int:
        """
        Returns the number of extra workers assigned to vespene.
        """
        return sum(base.vespene_workers_surplus for base in self.values())

    @property
    def mineral_workers_deficit(self) -> int:
        """
        Returns the number of workers that can still be assigned to minerals before saturation.
        """
        return sum(base.mineral_workers_deficit for base in self.values())

    @property
    def vespene_workers_deficit(self) -> int:
        """
        Returns the number of workers that can still be assigned to vespene before saturation.
        """
        return sum(base.vespene_workers_deficit for base in self.values())

    @property
    def with_available_workers(self) -> "Bases":
        """
        Returns bases that have workers above saturation.
        """
        return self.filter(lambda base: base.workers_available)

    @property
    def minerals_left(self) -> int:
        """
        Returns the number of minerals left in all bases.
        """
        return sum(base.minerals_left for base in self.values())

    @property
    def vespene_left(self) -> int:
        """
        Returns the number of vespene left in all bases.
        """
        return sum(base.vespene_left for base in self.values())

    def add(self, location: Point2 | list[Point2]) -> None:
        """
        Add a new base location to the collection.

        Args:
            location (Point2 | list[Point2]): The location of the bases.
        """
        if isinstance(location, Point2):
            location = [location]
        for loc in location:
            self[loc] = Base(self.__bot, loc)

    def filter(self, condition: Callable[[Base], bool]) -> "Bases":
        """
        Returns bases that satisfy a given condition.

        Eg.:
        ```python
            no_worker_bases = bases.filter(lambda base: base.mineral_workers == 0)
        ```

        Args:
            condition (Callable[[Base], bool]): A function that takes a Base and returns a bool.
        """
        filtered_bases = Bases(self.__bot)
        filtered_bases.update(
            {base: self[base] for base in self if condition(self[base])}
        )
        return filtered_bases

    def sorted(
        self, condition: Callable[[Base], bool], reverse: bool = False
    ) -> list[Base]:
        """
        Returns a list of bases sorted by a given condition.

        Eg.:
        ```python
            bases_by_minerals = bases.sorted(lambda base: base.minerals_left)
        ```

        Args:
            condition (Callable[[Base], bool]): A function that takes a Base and returns a bool.
            reverse (bool, optional): If set to True, the bases are sorted in descending order. Defaults to False.
        """
        return sorted(self.values(), key=condition, reverse=reverse)

    @get_positions
    def closest_to(self, location: Unit | Point2) -> Base:
        """
        Returns the base closest to the given location.
        """
        return self[location]

    @get_tags
    def contains_worker(self, worker: Unit | int) -> Base | None:
        """
        Returns the base that contains the given worker.
        """
        return next(
            (
                base
                for base in self.values()
                if worker in base.mineral_workers or worker in base.vespene_workers
            ),
            None,
        )

    def contains_resource(self, resource: Unit | int) -> Base | None:
        """
        Returns the base that contains the given resource.
        """
        resource = self.__get_unit(resource)
        return self.closest_to(resource)

    @get_tags
    def contains_structure(self, structure: Unit | int) -> Base | None:
        """
        Returns the base that contains the given structure.
        """
        return next(
            (base for base in self.values() if structure in base.structures),
            None,
        )

    @get_tags
    def contains_townhall(self, townhall: Unit | int) -> Base | None:
        """
        Returns the base that contains the given townhall.
        """
        return next(
            (base for base in self.values() if townhall in base.townhalls),
            None,
        )

    @get_tags
    def remove_worker(self, worker: Unit | int) -> None:
        """
        Removes the given worker from the base it is assigned to.
        """
        base = self.contains_worker(worker)
        if base:
            if worker in base.mineral_workers:
                base.remove_worker_from_minerals(worker)
            elif worker in base.vespene_workers:
                base.remove_worker_from_vespene(worker)

    def remove_structure(self, structure: Unit | int) -> None:
        """
        Removes the given structure from the base it is assigned to.
        """
        base = self.contains_structure(structure)
        if base:
            base.remove_structure(structure)

    def remove_townhall(self, townhall: Unit | int) -> None:
        """
        Removes the given townhall from the base it is assigned to.
        """
        base = self.contains_townhall(townhall)
        if base:
            base.remove_townhall(townhall)

    def remove_building(self, building: Unit | int) -> None:
        """
        Removes the given building from the base it is assigned to.
        """
        base = self.contains_structure(building)
        if not base:
            base = self.contains_townhall(building)
        if base:
            base.remove_structure(building)

    def assign_worker_to_resource(
        self, worker: Unit | int, resource: Unit | int
    ) -> None:
        """
        Assigns the given worker to the given resource.
        """
        resource = self.__get_unit(resource)
        base = self.contains_resource(resource)
        if base:
            if resource in base.mineral_fields:
                base.add_worker_to_minerals(worker)
            elif resource in base.refineries:
                base.add_worker_to_vespene(worker)

    def __get_unit(self, unit: Unit | int) -> Unit:
        return unit if isinstance(unit, Unit) else self.__bot.units.find_by_tag(unit)

    @get_positions
    def __getitem__(self, __key: Unit | Point2) -> Base:
        """
        Returns the base closest to the given location.
        """
        if __key not in self:
            __key = __key.closest(self.keys())
        return super().__getitem__(__key)


class Workers(dict[SCVAssignment, dict[int, int] | set[int]]):
    """
    ### Represents a collection of workers in the game.

    This class extends the built-in `dict` class and uses `SCVAssignment` as the key type.
    The values of the dictionary can be either a dictionary of integers or a set of integers,
    depending on the assignment type.

    ### Attributes:
    - mineral_miners (dict[int, int]): A dictionary of worker tags assigned to mineral mining.
    - vespene_miners (dict[int, int]): A dictionary of worker tags assigned to vespene gas mining.
    - builders (set[int]): A set of worker tags assigned to building construction.
    - scouts (set[int]): A set of worker tags assigned to scouting.
    - repairers (set[int]): A set of worker tags assigned to repairing.
    - army (set[int]): A set of worker tags assigned to army-related tasks.
    - none (set[int]): A set of worker tags with no specific assignment.

    ### Properties:
    - all (set[int]): Returns all workers.
    - mineral_tags (set[int]): Returns all mineral worker tags.
    - vespene_tags (set[int]): Returns all vespene worker tags.
    - total (int): Returns the total number of workers.

    ### Methods:
    - remove(worker: Unit | int, assignment: SCVAssignment = None) -> None: Removes the given worker from the given assignment.
    - add(worker: Unit | int, assignment: SCVAssignment, resource: Unit | int = None) -> None: Adds the given worker to the given assignment.
    - get_assignment(worker: Unit | int) -> SCVAssignment | None: Returns the current assignment of a worker.
    - change_assignment(worker: Unit | int, new_assignment: SCVAssignment, resource: Unit | int = None, is_new: bool = False, old_assignment: SCVAssignment = None) -> None: Change the assignment of a worker to a new assignment.
    - get_resource_tag(worker: Unit | int, assignment: SCVAssignment = None) -> int | None: Get the resource tag (mineral or vespene) assigned to the worker.
    - get_workers_for_resource(resource: Unit | int) -> set[int]: Returns the workers assigned to the given resource.
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
    def vespene_miners(self) -> dict[int, int]:
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

    @property
    def total(self) -> int:
        """
        Returns the total number of workers.
        """
        return len(self.all)

    @get_tags
    def remove(self, worker: Unit | int, assignment: SCVAssignment = None) -> None:
        """
        Removes the given worker from the given assignment.

        If the assignment is not provided, it will try to find it.
        """
        if not assignment:
            assignment = self.get_assignment(worker)

        if not assignment:
            return

        if assignment in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            del self[assignment][worker]
        else:
            self[assignment].remove(worker)

    @get_tags
    def add(
        self, worker: Unit | int, assignment: SCVAssignment, resource: Unit | int = None
    ) -> None:
        """
        Adds the given worker to the given assignment.

        If the assignment involves a resource, the resource must be provided.
        """
        if assignment in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            if not resource:
                raise ValueError(
                    f"Resource not provided for worker {worker} and assignment {assignment}"
                )
            self[assignment][worker] = resource
        else:
            self[assignment].add(worker)

    @get_tags
    def get_assignment(self, worker: Unit | int) -> SCVAssignment | None:
        """
        Returns the current assignment of a worker.
        """
        return next(
            (assignment for assignment, workers in self.items() if worker in workers),
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

    @get_tags
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

        return self[assignment][worker]

    @get_tags
    def get_workers_for_resource(self, resource: Unit | int) -> set[int]:
        """
        Get the workers assigned to the given resource.

        Args:
            resource (Unit | int): The resource unit or its tag.

        Returns:
            set[int]: The set of worker tags assigned to the given resource.
        """
        return {
            worker
            for worker, tag in self[SCVAssignment.MINERALS].items()
            if tag == resource
        } | {
            worker
            for worker, tag in self[SCVAssignment.VESPENE].items()
            if tag == resource
        }


# TODO: Implement better prediction models
@dataclass
class Economy:
    """
    ### Represents the economy of the game.

    ### Attributes:
    - bot (Sc2City): The instance of the Sc2City bot.
    - minerals_history (list[int]): The history of mineral values.
    - total_minerals_history (list[int]): The history of total mineral values.
    - total_minerals_spent (int): The total amount of minerals spent.
    - vespene_history (list[int]): The history of vespene values.
    - total_vespene_history (list[int]): The history of total vespene values.
    - total_vespene_spent (int): The total amount of vespene spent.
    - collection_interval (int): The interval at which the economy data is collected, measured in frames.
    - collection_limit (int): The maximum number of frames to keep in the history.
    - collection_frames (list[int]): The frames at which the economy data is collected.
    - last_training (int): The game loop at which the models were last trained.
    - models (tuple[LinearRegression]): The prediction models for mineral and vespene collection rates.

    ### Properties:
    - mineral_rate (float): The mineral collection rate in minerals per frame.
    - vespene_rate (float): The vespene collection rate in vespene per frame.
    - mineral_rate_per_worker (float): The mineral collection rate per worker in minerals per frame.
    - vespene_rate_per_worker (float): The vespene collection rate per worker in vespene per frame.
    - mineral_rate_per_base (float): The mineral collection rate per base in minerals per frame.
    - vespene_rate_per_base (float): The vespene collection rate per base in vespene per frame.

    ### Methods:
    - update() -> None: Update the economy data.
    - spend(minerals: int = None, vespene: int = None) -> None: Update the spent resources.
    - recover_resources(minerals: int = None, vespene: int = None) -> None: Update the recovered resources.
    - predict_frame(minerals: int = None, vespene: int = None) -> tuple[int, int]: Predict the frame at which the given resource will reach the given value.
    - calculate_frames_to_value(minerals: int = None, vespene: int = None) -> tuple[int, int]: Calculate the frames until the given resource reaches the given value.
    - train_models() -> None: Train the prediction models.
    """

    _bot: "Sc2City"

    minerals_history: list[int] = field(default_factory=list)
    total_minerals_history: list[int] = field(default_factory=list)
    total_minerals_spent: int = 0

    vespene_history: list[int] = field(default_factory=list)
    total_vespene_history: list[int] = field(default_factory=list)
    total_vespene_spent: int = 0

    collection_interval = 10  # Measured in frames
    collection_limit = 100
    collection_frames: list[int] = field(default_factory=list)
    last_training = 0

    models: tuple[LinearRegression] = None

    @staticmethod
    def __can_train_models(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._bot.state.game_loop < self.collection_interval * 10:
                return None
            if (
                self._bot.state.game_loop - self.last_training
                > self.collection_interval
                or not self.models
            ):
                self.train_models()
            return func(self, *args, **kwargs)

        return wrapper

    @__can_train_models
    @property
    def mineral_rate(self) -> float:
        """
        Returns the mineral collection rate in minerals per frame.
        """
        return self.models[0].coef_[0]

    @__can_train_models
    @property
    def vespene_rate(self) -> float:
        """
        Returns the vespene collection rate in vespene per frame.
        """
        return self.models[1].coef_[0]

    @property
    def mineral_rate_per_worker(self) -> float:
        """
        Returns the mineral collection rate per worker in minerals per frame.
        """
        return self.mineral_rate / len(self._bot.scvs.mineral_miners)

    @property
    def vespene_rate_per_worker(self) -> float:
        """
        Returns the vespene collection rate per worker in vespene per frame.
        """
        return self.vespene_rate / len(self._bot.scvs.vespene_miners)

    @property
    def mineral_rate_per_base(self) -> float:
        """
        Returns the mineral collection rate per base in minerals per frame.
        """
        return self.mineral_rate / len(self._bot.bases)

    @property
    def vespene_rate_per_base(self) -> float:
        """
        Returns the vespene collection rate per base in vespene per frame.
        """
        return self.vespene_rate / len(self._bot.bases)

    def mineral_rate_for_base(self, base: Base | Unit | Point2) -> float:
        """
        Returns the mineral collection rate per worker for a base in minerals per frame.
        """
        if not isinstance(base, Base):
            base = self._bot.bases[base]
        return self.mineral_rate_per_worker * len(base.mineral_workers)

    def vespene_rate_for_base(self, base: Base) -> float:
        """
        Returns the vespene collection rate per worker for a base in vespene per frame.
        """
        if not isinstance(base, Base):
            base = self._bot.bases[base]
        return self.vespene_rate_per_worker * len(base.vespene_workers)

    def update(self) -> None:
        """
        Update the economy data.
        """
        if self._bot.state.game_loop % self.collection_interval != 0:
            return

        self.minerals_history.append(self._bot.minerals)
        self.total_minerals_history.append(
            self._bot.minerals + self.total_minerals_spent
        )

        self.vespene_history.append(self._bot.vespene)
        self.total_vespene_history.append(self._bot.vespene + self.total_vespene_spent)

        self.collection_frames.append(self._bot.state.game_loop)

    def spend(self, minerals: int = None, vespene: int = None) -> None:
        """
        Update the spent resources.

        Args:
            minerals (int, optional): The amount of minerals spent. Defaults to None.
            vespene (int, optional): The amount of vespene spent. Defaults to None.
        """
        self.total_minerals_spent += minerals if minerals else 0
        self.total_vespene_spent += vespene if vespene else 0

    def recover_resources(self, minerals: int = None, vespene: int = None) -> None:
        """
        Update the recovered resources.

        Args:
            minerals (int, optional): The amount of minerals spent. Defaults to None.
            vespene (int, optional): The amount of vespene spent. Defaults to None.
        """
        self.total_minerals_spent -= minerals if minerals else 0
        self.total_vespene_spent -= vespene if vespene else 0

    @__can_train_models
    def predict_frame(
        self, minerals: int = None, vespene: int = None
    ) -> tuple[int, int]:
        """
        Predict the frame at which the given resource will reach the given value.

        Args:
            minerals (int, optional): The desired mineral value.
            vespene (int, optional): The desired vespene value.

        Returns:
            tuple[int, int]: The predicted frame for minerals and vespene.
        """
        predicted_mineral_time = self.__predict_frame(minerals) if minerals else None
        predicted_vespene_time = (
            self.__predict_frame(vespene, True) if vespene else None
        )
        time = self.__choose_max(predicted_mineral_time, predicted_vespene_time)
        return time

    @__can_train_models
    def calculate_frames_to_value(
        self, minerals: int = None, vespene: int = None
    ) -> tuple[int, int]:
        """
        Calculate frames until the given resource reaches the given value.

        Args:
            minerals (int, optional): The desired mineral value.
            vespene (int, optional): The desired vespene value.

        Returns:
            tuple[int, int]: The predicted frame for minerals and vespene.
        """
        calculated_mineral_frames = (
            self.__calculate_frames(minerals) if minerals else None
        )
        calculated_vespene_frames = (
            self.__calculate_frames(vespene, True) if vespene else None
        )
        frames = self.__choose_max(calculated_mineral_frames, calculated_vespene_frames)
        return frames

    def train_models(self) -> None:
        """
        Train the prediction models.
        """
        X = np.array(self.collection_frames[-self.collection_limit :]).reshape(-1, 1)
        Y = np.array(self.total_minerals_history[-self.collection_limit :])
        Y2 = np.array(self.total_vespene_history[-self.collection_limit :])
        mineral_model = LinearRegression().fit(X, Y)
        vespene_model = LinearRegression().fit(X, Y2)
        self.models = (mineral_model, vespene_model)
        self.last_training = self._bot.state.game_loop

    def __predict_frame(self, resource: int, is_gas: bool = False) -> int:
        """
        Predict the frame at which the given resource will reach the given value.
        """
        model = self.models[1] if is_gas else self.models[0]
        total_resource = (
            self.total_vespene_history[-1]
            if is_gas
            else self.total_minerals_history[-1]
        )
        current_resource = self._bot.vespene if is_gas else self._bot.minerals
        target_value = total_resource + resource - current_resource
        return (
            int((target_value - model.intercept_) / model.coef_[0])
            if model.coef_[0] != 0
            else np.inf
        )

    def __calculate_frames(self, resource: int, is_gas: bool = False) -> int:
        """
        Calculate how many frames until the given resource will reach the given value.
        """
        model = self.models[1] if is_gas else self.models[0]
        current_resource = self._bot.vespene if is_gas else self._bot.minerals
        target_value = resource - current_resource
        return int(target_value / model.coef_[0]) if model.coef_[0] != 0 else np.inf

    def __choose_max(
        self, mineral_frames: int | None, vespene_frames: int | None
    ) -> int | None:
        """
        Choose the maximum value between the given frames.
        """
        if mineral_frames and vespene_frames:
            return max(mineral_frames, vespene_frames)
        return mineral_frames if mineral_frames else vespene_frames
