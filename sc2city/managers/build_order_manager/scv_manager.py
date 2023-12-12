from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.data import Alert

from utils import SCVAssignment
from game_objects import BUILDING_PRIORITY, Order
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

    def worker_split_frame_zero(self) -> None:
        mineral_fields = self.bot.mineral_field.closer_than(
            distance=10, position=self.bot.start_location
        )
        workers = Units(self.bot.workers, self.bot)
        for mineral_field in mineral_fields:
            worker = workers.closest_to(mineral_field)
            self.__assign_worker_to_mineral_field(worker, mineral_field)
            workers.remove(worker)

        for worker in workers:
            mineral_field = mineral_fields.closest_to(worker)
            self.__assign_worker_to_mineral_field(worker, mineral_field)

    def move_scvs(self) -> None:
        self.__handle_alerts()
        self.__distribute_workers()
        self.__speed_mining()

    def execute_action(self, order: Order) -> bool:
        return True

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
            worker = self.__select_builder(position)
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
            self.__remove_from_list(tag, assignment)

    def __remove_from_list(self, scv_tag: int, assignment: SCVAssignment) -> None:
        if assignment in (SCVAssignment.MINERALS, SCVAssignment.VESPENE):
            del self.bot.scvs[assignment][scv_tag]
        else:
            self.bot.scvs[assignment].remove(scv_tag)

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
                worker = self.__select_worker(refinery.position)
                if worker:
                    self.bot.scvs[SCVAssignment.VESPENE][worker.tag] = refinery.tag
                    worker.gather(refinery)
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
            worker = self.__select_worker(position=position)
            if worker:
                worker.move(worker.position)
                return

    # TODO: Add logic to distribute workers between different lists
    def __handle_idle_workers(self) -> None:
        """
        Send idle worker to closest townhall that is not saturated.
        If no saturated townhall available send to closest.
        """
        for worker in self.bot.workers.idle:
            if worker.tag not in self.bot.scvs[SCVAssignment.BUILD]:
                cc = self.bot.townhalls.ready.not_flying.sorted(
                    lambda x: x.distance_to(worker)
                ).first
                mfs = self.bot.mineral_field.closer_than(10, cc)
                mf = mfs.closest_to(worker)
                self.bot.scvs[SCVAssignment.MINERALS][worker.tag] = mf.tag
                worker.gather(mf)
            elif worker.tag in self.bot.scvs[SCVAssignment.BUILD]:
                # TODO: Handle for different order status
                position = next(
                    order.target for order in self.bot.queue if order.tag == worker.tag
                )
                if worker.position != position:
                    worker.move(position)

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

    def __assign_worker_to_mineral_field(
        self, worker: Unit, mineral_field: Unit
    ) -> None:
        worker.gather(mineral_field)
        self.bot.scvs[SCVAssignment.MINERALS][worker.tag] = mineral_field.tag

    def __select_builder(self, position: Point2) -> Unit | None:
        # TODO: Add error handling for when there are no available workers
        # TODO: Add logic to select other types of SCV builders aside from mineral collectors
        worker = next(
            (
                w
                for w in self.bot.workers.sorted(lambda x: x.distance_to(position))
                if w.tag in self.bot.scvs[SCVAssignment.MINERALS]
                and not w.is_carrying_resource
            ),
            None,
        )
        if worker:
            del self.bot.scvs[SCVAssignment.MINERALS][worker.tag]
            self.bot.scvs[SCVAssignment.BUILD].add(worker.tag)
            worker.stop()  # Used to handle workers in the move method
        return worker

    # TODO: Merge this method with __select_builder
    def __select_worker(self, position: Point2) -> Unit | None:
        """
        Same as __select_contractor, but this is used for distributing workers.
        Removes scv tag from scvs[SCVAssignment.MINERALS].
        """
        worker = next(
            (
                w
                for w in self.bot.workers.sorted(lambda x: x.distance_to(position))
                if w.tag in self.bot.scvs[SCVAssignment.MINERALS]
                and not w.is_carrying_resource
            ),
            None,
        )
        if worker:
            del self.bot.scvs[SCVAssignment.MINERALS][worker.tag]
        return worker
