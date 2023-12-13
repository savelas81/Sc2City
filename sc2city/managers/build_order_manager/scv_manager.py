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

SCV_BUILDS = {
    AbilityId.TERRANBUILD_COMMANDCENTER,
    AbilityId.TERRANBUILD_SUPPLYDEPOT,
    AbilityId.TERRANBUILD_REFINERY,
    AbilityId.TERRANBUILD_BARRACKS,
    AbilityId.TERRANBUILD_ENGINEERINGBAY,
    AbilityId.TERRANBUILD_MISSILETURRET,
    AbilityId.TERRANBUILD_BUNKER,
    AbilityId.TERRANBUILD_SENSORTOWER,
    AbilityId.TERRANBUILD_GHOSTACADEMY,
    AbilityId.TERRANBUILD_FACTORY,
    AbilityId.TERRANBUILD_STARPORT,
    AbilityId.TERRANBUILD_ARMORY,
    AbilityId.TERRANBUILD_FUSIONCORE,
}


class SCVManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.speed_mining = SpeedMining(bot)
        self.scvs_per_refinery: int = 3
        self.max_gas_miners: int = 100
        self.next_point = None  # TODO: Remove this when refactoring scouting logic

    def worker_split_frame_zero(self) -> None:
        mineral_fields = self.bot.mineral_field.closer_than(
            distance=10, position=self.bot.start_location
        )
        workers = Units(self.bot.workers, self.bot)
        for mineral_field in mineral_fields:
            worker = workers.closest_to(mineral_field)
            self.__assign_worker_to_resource(worker, mineral_field)
            workers.remove(worker)

        for worker in workers:
            self.__assign_worker_to_resource(worker)

    def move_scvs(self) -> None:
        self.__handle_alerts()
        self.__move_scouts()
        self.__distribute_workers()
        self.__speed_mining()

    # TODO: Include more possible orders
    def execute_action(self, order: Order) -> bool:
        if order.id != CustomOrders.WORKER_TO_SCOUT:
            return True

        if not order.target and order.id:
            order.target = self.bot.enemy_start_locations[0]

        if not order.tag:
            worker = self.__select_worker(order.target, SCVAssignment.SCOUT)
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
            worker = self.__select_worker(position, SCVAssignment.BUILD)
            if not worker:
                return order.can_skip
            order.tag = worker.tag
        else:
            # TODO: Handle for when the worker is not found
            worker = self.bot.workers.find_by_tag(order.tag)

        if worker.is_using_ability(SCV_BUILDS):
            return True

        if self.bot.tech_requirement_progress(order.id) != 1 or not self.bot.can_afford(
            order.id
        ):
            return order.can_skip
        worker.build(order.id, order.target)
        return False

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
        possible_positions = self.bot.current_strategy.building_placements.lists[
            position_priority
        ]
        for position in possible_positions:
            if await self.bot.can_place_single(unit_id, position):
                return position
        # TODO: Handle for when all pre-defined positions are occupied
        return None

    # TODO: Implement this method
    def __can_select_builder(self, order: Order) -> bool:
        return True

    def __handle_alerts(self) -> None:
        if self.bot.alert(Alert.MineralsExhausted):
            self.__remove_miners(
                self.bot.mineral_field.tags,
                self.bot.scvs[SCVAssignment.MINERALS],
                SCVAssignment.MINERALS,
            )
        elif self.bot.alert(Alert.VespeneExhausted):
            self.__remove_miners(
                self.bot.gas_buildings.tags,
                self.bot.scvs[SCVAssignment.VESPENE],
                SCVAssignment.VESPENE,
            )

    # TODO: Test if this method is working for gas geysers
    def __remove_miners(
        self,
        resource_tags: set[int],
        scv_resource: dict[int, int],
        assignment: SCVAssignment,
    ) -> None:
        tags_to_remove = [
            scv_tag
            for scv_tag, resource_tag in scv_resource.items()
            if resource_tag not in resource_tags
        ]
        for tag in tags_to_remove:
            worker = self.bot.workers.find_by_tag(tag)
            self.__update_worker_assignment(worker, assignment)

    # TODO: Add logic to handle more than one scout
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
        for worker_tag in self.bot.scvs[SCVAssignment.MINERALS]:
            worker = self.bot.workers.find_by_tag(worker_tag)
            mineralfield_tag = self.bot.scvs[SCVAssignment.MINERALS][worker_tag]
            self.speed_mining.speed_mine_minerals_single(
                worker, mineralfield_tag, self.bot.scvs[SCVAssignment.MINERALS]
            )
        for worker_tag in self.bot.scvs[SCVAssignment.VESPENE]:
            worker = self.bot.workers.find_by_tag(worker_tag)
            if (
                not worker
            ):  # If worker is inside refinery it can't be found by find_by_tag
                continue
            vespene_tag = self.bot.scvs[SCVAssignment.VESPENE][worker_tag]
            self.speed_mining.speed_mine_gas_single(worker, vespene_tag)

    def __distribute_workers(self) -> None:
        self.__calculate_custom_assigned_workers()
        self.__handle_idle_workers()

        """
        manages saturation for refineries
        """
        for refinery in self.bot.gas_buildings.ready:
            """
            Assigns scv to gather vespene if needed
            """
            if (
                refinery.custom_assigned_harvesters < self.scvs_per_refinery
                and len(self.bot.scvs[SCVAssignment.VESPENE]) < self.max_gas_miners
            ):
                worker = self.__select_worker(
                    refinery.position, SCVAssignment.VESPENE, resource=refinery
                )
                if worker:
                    return

            """
            Stops scv from gathering vespene is needed. 
            Idle workers are given new assignment on next frame.
            """
            if (
                refinery.custom_assigned_harvesters > self.scvs_per_refinery
                or len(self.bot.scvs[SCVAssignment.VESPENE]) > self.max_gas_miners
            ):
                for worker in self.bot.workers.sorted(
                    lambda x: x.distance_to(refinery)
                ):
                    if worker.tag in self.bot.scvs[SCVAssignment.VESPENE]:
                        worker_target_refinery_tag = self.bot.scvs[
                            SCVAssignment.VESPENE
                        ][worker.tag]
                        if worker_target_refinery_tag == refinery.tag:
                            worker.move(worker.position)
                            del self.bot.scvs[SCVAssignment.VESPENE][worker.tag]
                            return

        """
        Stops scv from over saturated townhall if under saturated townhall is available.
        Stops only if custom_surplus_harvesters > 1 to prevent workers changing mining locations unnecessary.
        Idle workers are given new assignment on next frame.
        """
        townhall_with_surplus_harvesters = next(
            (
                t
                for t in self.bot.townhalls.ready.not_flying.sorted(
                    lambda x: x.custom_surplus_harvesters, reverse=True
                )
                if t.custom_surplus_harvesters > 1
            ),
            None,
        )
        if townhall_with_surplus_harvesters and self.bot.townhalls.filter(
            lambda x: x.custom_surplus_harvesters < 0
        ):
            position = self.bot.mineral_field.closer_than(
                10, townhall_with_surplus_harvesters.postion
            ).center
            worker = self.__select_worker(from_position=position)
            if worker:
                worker.move(worker.position)
                return

    # TODO: Add handlers for other worker assignments
    # TODO: Refactor scout logic
    def __handle_idle_workers(self) -> None:
        """
        Send idle worker to closest townhall that is not saturated.
        If no saturated townhall available send to closest.
        """
        for worker in self.bot.workers.idle:
            if worker.tag in self.bot.scvs[SCVAssignment.BUILD]:
                # TODO: Handle for different order status
                position = next(
                    order.target for order in self.bot.queue if order.tag == worker.tag
                )
                if worker.position != position:
                    worker.move(position)
            elif (
                worker.tag in self.bot.scvs[SCVAssignment.SCOUT]
                and self.bot.pending_scouting_points is not None
            ):
                continue
            else:
                self.__update_worker_assignment(worker)

    def __calculate_custom_assigned_workers(self) -> None:
        """
        Calculate custom_assigned_harvesters for CC, REFINERY and MINERALFIELD
        This is needed because we get wrong information from API when using speedmining
        """
        for structure in (
            self.bot.gas_buildings
            | self.bot.townhalls.ready.not_flying
            | self.bot.mineral_field
        ):
            structure.custom_assigned_harvesters = 0
            structure.custom_surplus_harvesters = 0
        for target_refinery_tag in self.bot.scvs[SCVAssignment.VESPENE].values():
            refinery = self.bot.gas_buildings.ready.find_by_tag(target_refinery_tag)
            if refinery:
                refinery.custom_assigned_harvesters += 1
                continue
        for target_mf_tag in self.bot.scvs[SCVAssignment.MINERALS]:
            mf = self.bot.mineral_field.find_by_tag(target_mf_tag)
            if mf:
                mf.custom_assigned_harvesters += 1
                cc = self.bot.townhalls.ready.not_flying.closest_to(mf)
                cc.custom_assigned_harvesters += 1
                continue

        for refinery in self.bot.gas_buildings.ready:
            refinery.custom_surplus_harvesters = refinery.custom_assigned_harvesters - 3
        for cc in self.bot.townhalls.ready.not_flying:
            mfs_amount = self.bot.mineral_field.closer_than(10, cc).amount
            cc.custom_surplus_harvesters = cc.custom_assigned_harvesters - (
                mfs_amount * 2
            )
        for mf in self.bot.mineral_field:
            mf.custom_surplus_harvesters = mf.custom_assigned_harvesters - 2

    def __select_worker(
        self,
        from_position: Point2 = None,
        to_assignment: SCVAssignment = None,
        from_assignment: SCVAssignment = SCVAssignment.MINERALS,
        resource: Unit = None,
    ) -> Unit | None:
        """
        Selects a worker to be assigned to a new task.

        Args:
            from_position (Point2, optional): The position from which to select the worker. Defaults to None.
            to_assignment (SCVAssignment, optional): The new assignment for the worker. Defaults to None.
            from_assignment (SCVAssignment, optional): The current assignment of the worker. Defaults to SCVAssignment.MINERALS.
            resource (Unit, optional): The resource unit associated with the assignment (e.g., mineral field or refinery).
                If not provided, the closest refinery or mineral field to the worker will be assigned.

        Returns:
            Unit | None: The selected worker unit, or None if no worker is available.
        """
        if not from_position:
            from_position = self.bot.start_location
        worker = next(
            (
                w
                for w in self.bot.workers.sorted(lambda x: x.distance_to(from_position))
                if w.tag in self.bot.scvs[from_assignment]
                and not w.is_carrying_resource
            ),
            None,
        )
        if not worker:
            return None
        if to_assignment:
            self.__update_worker_assignment(
                worker, from_assignment, to_assignment, resource
            )
        return worker

    def __update_worker_assignment(
        self,
        worker: Unit,
        from_assignment: SCVAssignment = None,
        to_assignment: SCVAssignment = SCVAssignment.MINERALS,
        resource: Unit = None,
    ) -> None:
        """
        Updates worker assignment.

        Args:
            worker (Unit): The worker unit to update the assignment for.
            from_assignment (SCVAssignment): The current assignment of the worker. Defaults to NONE.
            to_assignment (SCVAssignment, optional): The new assignment for the worker. Defaults to SCVAssignment.MINERALS.
            resource (Unit, optional): The resource unit associated with the assignment (e.g., mineral field or gas geyser).
                Defaults to None.
        """
        if not from_assignment:
            from_assignment = self.__find_assignment(worker)

        if not from_assignment:
            pass
        elif from_assignment in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            del self.bot.scvs[from_assignment][worker.tag]
        else:
            self.bot.scvs[from_assignment].remove(worker.tag)

        if to_assignment in {SCVAssignment.MINERALS, SCVAssignment.VESPENE}:
            self.__assign_worker_to_resource(worker, resource)
        else:
            self.bot.scvs[to_assignment].add(worker.tag)
            worker.stop()  # Stops worker from executing previous command to be handled by the idle handler in the next frame

    def __find_assignment(self, worker: Unit) -> SCVAssignment | None:
        """
        Finds the current assignment of a worker.

        Args:
            worker (Unit): The worker unit to find the assignment for.

        Returns:
            SCVAssignment: The current assignment of the worker.
        """
        for assignment, workers in self.bot.scvs.items():
            if worker.tag in workers:
                return assignment
        return None

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
            resource = self.__find_closest_resource(worker, SCVAssignment.MINERALS)
        elif not resource:
            resource = self.__find_closest_resource(worker, assignment)
        if not assignment:
            assignment = (
                SCVAssignment.MINERALS
                if resource.is_mineral_field
                else SCVAssignment.VESPENE
            )
        worker.gather(resource)
        self.bot.scvs[assignment][worker.tag] = resource.tag

    # TODO: Test if it's not including exhausted refinery
    def __find_closest_resource(self, worker: Unit, assignment: SCVAssignment) -> Unit:
        """
        Finds the closest resource to the worker.

        Args:
            worker (Unit): The worker unit.
            assignment (SCVAssignment): The assignment type.

        Returns:
            Unit: The closest resource unit.
        """
        for townhall in self.bot.townhalls.ready.not_flying.sorted_by_distance_to(
            worker
        ):
            resources = (
                self.bot.mineral_field
                if assignment == SCVAssignment.MINERALS
                else self.bot.gas_buildings.ready
            ).closer_than(10, townhall)
            if resources:
                return resources.closest_to(worker)

        resources = (
            self.bot.mineral_field
            if assignment == SCVAssignment.MINERALS
            else self.bot.gas_buildings.ready
        )
        return resources.closest_to(worker)
