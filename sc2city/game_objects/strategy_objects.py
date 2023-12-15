import enum
import numpy as np
import functools
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

from sc2.bot_ai import BotAI
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2

from sklearn.linear_model import LinearRegression

from .building_placements import BuildingPlacements
from utils import BuildTypes, OrderType, Status, SCVAssignment

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


@dataclass
class Economy:
    """
    Represents the economy of the bot in the Starcraft 2 game.

    Attributes:
        bot (BotAI): The instance of the bot.
        mineral_history (list[int]): The history of mineral values.
        total_minerals_history (list[int]): The history of total mineral values.
        minerals_spent_since_last_collection (int): The amount of minerals spent since the last collection.
        vespene_history (list[int]): The history of vespene values.
        total_vespene_history (list[int]): The history of total vespene values.
        vespene_spent_since_last_collection (int): The amount of vespene spent since the last collection.
        collection_interval (int): The interval between data collection (measured in frames).
        collection_limit (int): The maximum number of data points to keep in the history.
        collection_frames (list[int]): The frames at which the data was collected.
        last_training (int): The game loop at which the models were last trained.
        models (tuple[LinearRegression]): The trained linear regression models for mineral and vespene prediction.

    Properties:
        total_minerals_spent (int): Total minerals spent in the game.
        total_vespene_spent (int): Total vespene spent in the game.
        mineral_rate (float): The mineral collection rate in minerals per frame.
        vespene_rate (float): The vespene collection rate in vespene per frame.
        mineral_rate_per_worker (float): The mineral collection rate per worker in minerals per frame.
        vespene_rate_per_worker (float): The vespene collection rate per worker in vespene per frame.
        mineral_rate_per_base (float): The mineral collection rate per base in minerals per frame.
        vespene_rate_per_base (float): The vespene collection rate per base in vespene per frame.

    Methods:
        update(): Update the economy data.
        spend_resources(minerals: int = None, vespene: int = None): Update the spent resources.
        predict_frame(minerals: int = None, vespene: int = None): Predict the frame at which the given resource will reach the given value.
        train_model(): Train the prediction models.
    """

    bot: "Sc2City"

    mineral_history: list[int] = field(default_factory=list)
    total_minerals_history: list[int] = field(default_factory=list)
    minerals_spent_since_last_collection: int = 0
    total_minerals_spent: int = 0

    vespene_history: list[int] = field(default_factory=list)
    total_vespene_history: list[int] = field(default_factory=list)
    vespene_spent_since_last_collection: int = 0
    total_vespene_spent: int = 0

    collection_interval = 10  # Measured in frames
    collection_limit = 100
    collection_frames: list[int] = field(default_factory=list)
    last_training = 0
    models: tuple[LinearRegression] = None

    @staticmethod
    def __can_train_model(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if (
                self.bot.state.game_loop - self.last_training > self.collection_interval
                or not self.__models
            ):
                self.train_model()
            return func(self, *args, **kwargs)

        return wrapper

    @property
    def total_minerals_spent(self) -> int:
        """
        Total minerals spent in the game.
        """
        return self.total_minerals_history[-1] - self.bot.minerals

    @property
    def total_vespene_spent(self) -> int:
        """
        Total vespene spent in the game.
        """
        return self.total_vespene_history[-1] - self.bot.vespene

    @__can_train_model
    @property
    def mineral_rate(self) -> float:
        """
        Returns the mineral collection rate in minerals per frame.
        """
        return self.__models[0].coef_

    @__can_train_model
    @property
    def vespene_rate(self) -> float:
        """
        Returns the vespene collection rate in vespene per frame.
        """
        return self.__models[1].coef_

    @property
    def mineral_rate_per_worker(self) -> float:
        """
        Returns the mineral collection rate per worker in minerals per frame.
        """
        return self.mineral_rate / len(self.bot.scvs.mineral_miners)

    @property
    def vespene_rate_per_worker(self) -> float:
        """
        Returns the vespene collection rate per worker in vespene per frame.
        """
        return self.vespene_rate / len(self.bot.scvs.vespene_miners)

    @property
    def mineral_rate_per_base(self) -> float:
        """
        Returns the mineral collection rate per base in minerals per frame.
        """
        return self.mineral_rate / len(self.bot.bases)

    @property
    def vespene_rate_per_base(self) -> float:
        """
        Returns the vespene collection rate per base in vespene per frame.
        """
        return self.vespene_rate / len(self.bot.bases)

    @property
    def mineral_rate_for_base(self, base: Base) -> float:
        """
        Returns the mineral collection rate per worker per base in minerals per frame.
        """
        return self.mineral_rate_per_worker * len(base.mineral_workers)

    @property
    def vespene_rate_for_base(self, base: Base) -> float:
        """
        Returns the vespene collection rate per worker per base in vespene per frame.
        """
        return self.vespene_rate_per_worker * len(base.vespene_workers)

    def update(self) -> None:
        """
        Update the economy data.
        """
        if self.bot.state.game_loop % self.collection_interval != 0:
            return

        self.mineral_history.append(self.bot.minerals)
        self.total_minerals_history.append(
            self.bot.minerals + self.total_minerals_spent
        )

        self.vespene_history.append(self.bot.vespene)
        self.total_vespene_history.append(self.bot.vespene + self.total_vespene_spent)

        self.collection_frames.append(self.bot.state.game_loop)

    def spend_resources(self, minerals: int = None, vespene: int = None) -> None:
        """
        Update the spent resources.

        Args:
            minerals (int, optional): The amount of minerals spent. Defaults to None.
            vespene (int, optional): The amount of vespene spent. Defaults to None.
        """
        self.total_minerals_spent += minerals if minerals else 0
        self.total_vespene_spent += vespene if vespene else 0

    @__can_train_model
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
        predicted_mineral_time = (
            self.__predict_frame(self.bot.minerals) if minerals else None
        )
        predicted_vespene_time = (
            self.__predict_frame(self.bot.vespene, True) if vespene else None
        )
        return predicted_mineral_time, predicted_vespene_time

    def train_model(self) -> None:
        """
        Train the prediction models.
        """
        X = np.array(self.collection_frames[-self.collection_limit :]).reshape(-1, 1)
        Y = np.array(self.total_minerals_history[-self.collection_limit :])
        Y2 = np.array(self.total_vespene_history[-self.collection_limit :])
        mineral_model = LinearRegression().fit(X, Y)
        vespene_model = LinearRegression().fit(X, Y2)
        self.__models = (mineral_model, vespene_model)
        self.last_training = self.bot.state.game_loop

    def __predict_frame(self, resource: int, is_gas: bool = False) -> int:
        """
        Predict the frame at which the given resource will reach the given value.
        """
        model = self.__models[1] if is_gas else self.__models[0]
        total_resource = (
            self.total_vespene_history[-1]
            if is_gas
            else self.total_minerals_history[-1]
        )
        current_resource = self.bot.vespene if is_gas else self.bot.minerals
        target_value = total_resource + resource - current_resource
        return (
            int((target_value - model.intercept_) / model.coef_)
            if model.coef_ != 0
            else np.inf
        )
