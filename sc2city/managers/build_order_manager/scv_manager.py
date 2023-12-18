import math
import numpy as np
from copy import copy
from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.data import Alert

from utils import SCVAssignment, Status
from game_objects import BUILDING_PRIORITY, Order, CustomOrders
from .speed_mining import SpeedMining

if TYPE_CHECKING:
    from Sc2City import Sc2City


class SCVManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.speed_mining = SpeedMining(bot)
        self.scvs_per_refinery: int = 3
        self.max_gas_miners: int = 100
        self.worker_speed: float = 0.12555803571428573  # Measured in frames
        self.next_point = None  # TODO: Remove this when refactoring scouting logic

    def worker_split_frame_zero(self) -> None:
        mineral_fields = self.bot.bases[self.bot.start_location].mineral_fields
        # Why are we doing this instead of self.bot.workers?
        workers = Units(self.bot.workers, self.bot)
        for mineral_field in mineral_fields:
            worker = workers.closest_to(mineral_field)
            self.__assign_worker_to_resource(worker, mineral_field)
            workers.remove(worker)

        for worker in workers:
            mineral_field = self.bot.mineral_field.closest_to(worker)
            self.__assign_worker_to_resource(worker, mineral_field)
        self.worker_speed = worker.distance_per_step / self.bot.client.game_step

    def move_scvs(self) -> None:
        self.__handle_alerts()
        self.__move_scouts()  # TODO: Move this to scripts when implemented
        self.__distribute_workers()
        self.__speed_mining()
        self.__handle_idle_workers()

    # TODO: Include more possible orders
    # TODO: Create a method to calculate resources spent on repairs
    def execute_action(self, order: Order) -> bool:
        if order.id != CustomOrders.WORKER_TO_SCOUT:
            return True

        if not order.target and order.id:
            order.target = self.bot.enemy_start_locations[0]

        if not order.tag:
            worker = self.select_worker(order.target, SCVAssignment.SCOUT)
            if not worker:
                return order.can_skip
            order.tag = worker.tag
        else:
            worker = self.bot.workers.find_by_tag(order.tag)
            if worker.is_using_ability(AbilityId.MOVE):
                order.update_status(Status.STARTED)
                return True
        worker.move(order.target)
        return False

    # TODO: Handle for cases where the build command is not successful, since
    # the API does't return anything (maybe check if resources are being spent)
    async def scv_build(self, order: Order) -> bool:
        """
        Returns False When executing orders to avoid double commands.
        """
        if not order.target:
            order.target = await self.__get_build_position(order.id)

        if not order.tag:
            if not self.__can_select_builder(order):
                return order.can_skip
            if order.id == UnitTypeId.REFINERY:
                position = order.target.position
            else:
                position = order.target
            worker = self.select_worker(position, SCVAssignment.BUILD)
            if not worker:
                return order.can_skip
            order.tag = worker.tag
        else:
            worker = self.bot.workers.find_by_tag(order.tag)
            if not worker:
                return order.can_skip

        if worker.is_constructing_scv:
            return True

        if self.bot.tech_requirement_progress(order.id) != 1 or not self.bot.can_afford(
            order.id
        ):
            return order.can_skip
        worker.build(order.id, order.target)
        # TODO: Move this to some placeholder confirmation logic
        # TODO: Calculate when placeholder is cancelled and return resources
        cost = self.bot.calculate_cost(order.id)
        self.bot.economy.spend(cost.minerals, cost.vespene)
        return False

    def select_worker(
        self,
        from_position: Point2 = None,
        to_assignment: SCVAssignment = None,
        from_assignment: SCVAssignment = SCVAssignment.MINERALS,
        resource: Unit = None,
    ) -> Unit | None:
        """
        ### Selects a worker to be assigned to a new task.

        ### Args:
        - from_position (Point2, optional): The position from which to select the worker. Defaults to None.
        - to_assignment (SCVAssignment, optional): The new assignment for the worker. Defaults to None.
        - from_assignment (SCVAssignment, optional): The current assignment of the worker. Defaults to SCVAssignment.MINERALS.
        - resource (Unit, optional): The resource unit associated with the assignment (e.g., mineral field or refinery).
            If not provided, the closest refinery or mineral field to the worker will be assigned.

        ### Returns:
        - Unit | None: The selected worker unit, or None if no worker is available.
        """
        if not from_position:
            from_position = self.bot.start_location
        worker = next(
            (
                worker
                for worker in self.bot.workers.sorted(
                    lambda x: x.distance_to(from_position)
                )
                if worker.tag in self.bot.scvs[from_assignment]
                and not worker.is_carrying_resource
            ),
            None,
        )
        if not worker:
            return None
        if to_assignment:
            self.update_worker_assignment(
                worker, from_assignment, to_assignment, resource
            )
        return worker

    def update_worker_assignment(
        self,
        worker: Unit | int,
        from_assignment: SCVAssignment = None,
        to_assignment: SCVAssignment = SCVAssignment.NONE,
        resource: Unit = None,
    ) -> None:
        """
        ### Updates worker assignment.

        ### Args:
        - worker (Unit, int): The worker unit or tag to update the assignment for.
        - from_assignment (SCVAssignment): The current assignment of the worker. If not provided, it will try to find the worker's current assignment.
        - to_assignment (SCVAssignment, optional): The new assignment for the worker. Defaults to SCVAssignment.NONE.
        - resource (Unit, optional): The resource unit associated with the assignment (e.g., mineral field or gas geyser). Defaults to None.
        """
        worker = (
            worker if isinstance(worker, Unit) else self.bot.workers.find_by_tag(worker)
        )

        if not from_assignment:
            from_assignment = self.bot.scvs.get_assignment(worker)

        self.bot.scvs.remove(worker.tag, from_assignment)
        if from_assignment in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            self.bot.bases.remove_worker(worker.tag)

        if to_assignment in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            self.__assign_worker_to_resource(worker, resource, to_assignment)
        else:
            self.bot.scvs.add(worker.tag, to_assignment)
            worker.stop()  # Stops worker from executing previous command to be handled by the idle handler in the next frame

    async def __get_build_position(self, unit_id: UnitTypeId) -> Point2 | Unit:
        if unit_id == UnitTypeId.REFINERY:
            for cc in self.bot.townhalls:
                geysers = self.bot.vespene_geyser.closer_than(10.0, cc)
                for geyser in geysers:
                    if await self.bot.can_place_single(
                        UnitTypeId.REFINERY, geyser.position
                    ):
                        return geyser
            # TODO: Handle for when no geysers are available
            return None

        position_priority = BUILDING_PRIORITY[unit_id]
        possible_positions = self.bot.current_strategy.building_placements[
            position_priority
        ]
        for position in possible_positions:
            if await self.bot.can_place_single(unit_id, position):
                return position
        # TODO: Handle for when all pre-defined positions are occupied
        return None

    # TODO: Improve selection criteria
    def __can_select_builder(self, order: Order) -> bool:
        worker = self.select_worker(order.target)
        if not worker:
            return False

        target = (
            order.target if isinstance(order.target, Point2) else order.target.position
        )
        cost = self.bot.calculate_cost(order.id)
        distance = self.bot.distance_math_hypot(worker.position, target)
        time = distance / self.worker_speed
        frames_until_resources = self.bot.economy.calculate_frames_to_value(
            cost.minerals, cost.vespene
        )
        if not frames_until_resources:
            return False
        return time > frames_until_resources

    def __handle_alerts(self) -> None:
        """
        Handle alerts from the game.

        Vespene workers are idle when the refinery is exhausted and should be handled by the appropriate method instead.
        """
        if self.bot.alert(Alert.MineralsExhausted):
            tags_to_remove = {
                worker_tag
                for worker_tag, resource_tag in self.bot.scvs.mineral_miners.items()
                if resource_tag not in self.bot.mineral_field.tags
            }
            for tag in tags_to_remove:
                worker = self.bot.workers.find_by_tag(tag)
                self.update_worker_assignment(worker, SCVAssignment.MINERALS)

    # TODO: Move this to scripts when implemented
    def __move_scouts(self) -> None:
        scout = None
        for scout_tag in self.bot.scvs[SCVAssignment.SCOUT]:
            scout = self.bot.units.find_by_tag(scout_tag)
            break
        if not scout:
            return

        if self.bot.pending_scouting_points is not None:
            if self.bot.pending_scouting_points.any():
                if scout.type_id == UnitTypeId.REAPER:
                    grid = copy(self.bot.map_analyzer.reaper_grid)
                elif scout.is_flying:
                    grid = copy(self.bot.map_analyzer.enemy_air_grid)
                else:
                    grid = copy(self.bot.map_analyzer.enemy_ground_grid)
                condition_list = [
                    self.bot.pending_scouting_points == 1,
                    self.bot.pending_scouting_points != 1,
                ]
                choice_list = [grid, math.inf]
                scouting_grid = np.select(condition_list, choice_list)
                lowest_cost_points = (
                    self.bot.map_analyzer.map_data.lowest_cost_points_array(
                        from_pos=scout.position, radius=500, grid=scouting_grid
                    )
                )

                if self.bot.iteration % 4 == 0:
                    self.next_point = (
                        self.bot.map_analyzer.map_data.closest_towards_point(
                            points=lowest_cost_points, target=scout.position
                        )
                    )
                if self.next_point is not None and self.next_point.any():
                    path = self.bot.map_analyzer.map_data.pathfind(
                        start=scout.position.rounded,
                        goal=self.next_point,
                        grid=grid,
                        sensitivity=3,
                    )
                    if path is not None and len(path) > 0:
                        scout.move(path[0])
                else:
                    # logger.info(f"No self.next_point {str(self.next_point)}")
                    return

    def __speed_mining(self) -> None:
        for worker_tag, mineral_field_tag in self.bot.scvs.mineral_miners.items():
            worker = self.bot.workers.find_by_tag(worker_tag)
            self.speed_mining.speed_mine_minerals_single(
                worker, mineral_field_tag, self.bot.scvs.mineral_miners
            )
        for worker_tag, vespene_tag in self.bot.scvs.vespene_miners.items():
            worker = self.bot.workers.find_by_tag(worker_tag)
            if not worker:
                continue  # If worker is inside refinery it can't be found by find_by_tag
            self.speed_mining.speed_mine_gas_single(worker, vespene_tag)

    def __distribute_workers(self) -> None:
        """
        Distributes workers between bases.
        """
        self.__distribute_gas_workers()
        self.__distribute_mineral_workers()

    def __distribute_mineral_workers(self) -> None:
        """
        Distributes mineral workers between bases.
        """
        for base in self.bot.bases.owned.values():
            for _ in range(base.mineral_workers_surplus):
                if self.bot.bases.owned.mineral_workers_deficit < 1:
                    return
                self.select_worker(base.location, SCVAssignment.NONE)

    def __distribute_gas_workers(self) -> None:
        """
        Distributes gas workers between bases.
        """
        extra_workers = len(self.bot.scvs.vespene_miners) - self.max_gas_miners
        if extra_workers > 0:
            for _ in range(extra_workers):
                self.select_worker(
                    to_assignment=SCVAssignment.NONE,
                    from_assignment=SCVAssignment.VESPENE,
                )
            return

        for refinery in self.bot.gas_buildings.ready:
            if not refinery.has_vespene:
                continue

            workers = len(self.bot.scvs.get_workers_for_resource(refinery.tag))
            if workers > self.scvs_per_refinery:
                for _ in range(workers - self.scvs_per_refinery):
                    self.select_worker(
                        refinery.position, SCVAssignment.NONE, SCVAssignment.VESPENE
                    )

            if workers < self.scvs_per_refinery:
                for _ in range(self.scvs_per_refinery - workers):
                    self.select_worker(
                        refinery.position, SCVAssignment.VESPENE, resource=refinery
                    )

    # TODO: Add handlers for other worker assignments
    # TODO: Refactor scout logic
    # TODO: Handle for different order status
    def __handle_idle_workers(self) -> None:
        """
        Send idle worker to closest townhall that is not saturated.
        If no saturated townhall available send to closest.
        """
        for worker in self.bot.workers.idle:
            if worker.tag in self.bot.scvs.builders:
                position = next(
                    order.target for order in self.bot.queue if order.tag == worker.tag
                )
                if worker.position != position:
                    worker.move(position)
            elif (
                worker.tag in self.bot.scvs.scouts
                and self.bot.pending_scouting_points is not None
            ):
                continue
            else:
                self.update_worker_assignment(
                    worker, to_assignment=SCVAssignment.MINERALS
                )

    def __assign_worker_to_resource(
        self, worker: Unit, resource: Unit = None, assignment: SCVAssignment = None
    ) -> None:
        """
        Assigns a worker to a target unit for gathering resources. If no resource and no assignment
        are provided, the worker will be assigned to the closest mineral field.

        Args:
            worker (Unit): The worker unit to assign.
            resource (Unit, optional): The target resource to assign the worker to. If not provided,
                the closest resource to the worker will be assigned.
            assignment (SCVAssignment, optional): The assignment type to update the worker with.
                Defaults to None.

        Returns:
            None
        """
        if not resource and not assignment:
            resource = self.__find_best_resource(SCVAssignment.MINERALS)
        elif not resource:
            resource = self.__find_best_resource(assignment)
        if not assignment:
            assignment = (
                SCVAssignment.MINERALS
                if resource.is_mineral_field
                else SCVAssignment.VESPENE
            )
        worker.gather(resource)
        self.bot.scvs.add(worker, assignment, resource)
        self.bot.bases.assign_worker_to_resource(worker, resource)

    def __find_best_resource(self, assignment: SCVAssignment) -> Unit:
        """
        Finds the resource in base with the least amount of workers.

        Args:
            worker (Unit): The worker unit.
            assignment (SCVAssignment): The assignment type.

        Returns:
            Unit: The closest resource unit.
        """
        if assignment == SCVAssignment.VESPENE:
            base = self.bot.bases.owned.sorted(
                lambda base: base.vespene_workers_deficit, reverse=True
            )[0]
            return min(
                base.refineries.ready,
                key=lambda refinery: len(
                    self.bot.scvs.get_workers_for_resource(refinery)
                ),
            )

        base = self.bot.bases.owned.sorted(
            lambda base: base.mineral_workers_deficit, reverse=True
        )[0]
        return min(
            base.mineral_fields,
            key=lambda mineral: len(self.bot.scvs.get_workers_for_resource(mineral)),
        )
