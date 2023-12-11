from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId

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
        self.__distribute_workers()
        self.__speed_mining()

    # TODO: Handle for cases where the build command is not successful, since
    # the API does't return anything (maybe check if resources are being spent)
    async def scv_build(self, order: Order) -> bool:
        """
        Returns False When executing orders to avoid double commands.
        """
        if not order.target:
            order.target = await self.__get_build_position(order.id)

        if not order.worker_tag:
            if not self.__can_select_builder(order):
                return order.can_skip
            if order.id == UnitTypeId.REFINERY:
                position = order.target.position
            else:
                position = order.target
            # TODO: Handle for when the worker is not found
            worker = self.__select_builder(position)
            order.worker_tag = worker.tag

        # TODO: Handle for when the worker is not found
        # TODO: Handle for cases when worker is selected and can start building in the same frame
        worker = self.bot.workers.find_by_tag(order.worker_tag)
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

    def __speed_mining(self) -> None:
        for worker_tag in self.bot.mineral_collector_dict:
            worker = self.bot.workers.find_by_tag(worker_tag)
            mineral_tag = self.bot.mineral_collector_dict[worker_tag]
            self.speed_mining.speed_mine_minerals_single(
                worker, mineral_tag, self.bot.mineral_collector_dict
            )
        for worker_tag in self.bot.vespene_collector_dict:
            worker = self.bot.workers.find_by_tag(worker_tag)
            if (
                not worker
            ):  #  If worker is inside refinery it can't be found by find_by_tag
                continue
            if (
                not worker
            ):  #  If worker is inside refinery it can't be found by find_by_tag
                continue
            vespene_tag = self.bot.vespene_collector_dict[worker_tag]
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
                and len(self.bot.vespene_collector_dict) < self.max_gas_miners
            ):
                worker = self.__select_worker(refinery.position)
                if worker:
                    self.bot.vespene_collector_dict[worker.tag] = refinery.tag
                    worker.gather(refinery)
                    return

            """
            Stops scv from gathering vespene is needed. 
            Idle workers are given new assignment on next frame.
            """
            if (
                refinery.custom_assigned_harvesters > self.scvs_per_refinery
                or len(self.bot.vespene_collector_dict) > self.max_gas_miners
            ):
                for worker in self.bot.workers.sorted(
                    lambda x: x.distance_to(refinery)
                ):
                    if worker.tag in self.bot.vespene_collector_dict:
                        worker_target_refinery_tag = self.bot.vespene_collector_dict[
                            worker.tag
                        ]
                        if worker_target_refinery_tag == refinery.tag:
                            worker.move(worker.position)
                            del self.bot.vespene_collector_dict[worker.tag]
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
            if worker.tag not in self.bot.contractors:
                cc = self.bot.townhalls.ready.not_flying.sorted(
                    lambda x: x.distance_to(worker)).filter(
                    lambda x: x.custom_surplus_harvesters < 0).first
                if cc:
                    mfs = self.bot.mineral_field.closer_than(10, cc.position)
                    mf = mfs.closest_to(worker)
                    self.bot.mineral_collector_dict[worker.tag] = mf.tag
                    worker.gather(mf)
                    return
                cc = self.bot.townhalls.ready.not_flying.sorted(
                    lambda x: x.distance_to(worker)
                ).first
                mfs = self.bot.mineral_field.closer_than(10, cc)
                mf = mfs.closest_to(worker)
                self.bot.mineral_collector_dict[worker.tag] = mf.tag
                worker.gather(mf)
                return
            elif worker.tag in self.bot.contractors:
                # TODO: Handle for different order status
                position = next(
                    order.target
                    for order in self.bot.queue
                    if order.worker_tag == worker.tag
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
        for target_refinery_tag in self.bot.vespene_collector_dict.values():
            refinery = self.bot.gas_buildings.ready.find_by_tag(target_refinery_tag)
            if refinery:
                refinery.custom_assigned_harvesters += 1
                continue
        for target_mf_tag in self.bot.mineral_collector_dict:
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
        self.bot.mineral_collector_dict[worker.tag] = mineral_field.tag

    def __select_builder(self, position: Point2) -> Unit:
        # TODO: Add error handling for when there are no available workers
        # TODO: Add logic to select other types of SCV contractors aside from mineral collectors
        worker = next(
            (
                w
                for w in self.bot.workers.sorted(lambda x: x.distance_to(position))
                if w.tag in self.bot.mineral_collector_dict
                and not w.is_carrying_resource
            ),
            None,
        )
        if worker:
            del self.bot.mineral_collector_dict[worker.tag]
            self.bot.contractors.append(worker.tag)
            worker.stop()  # Used to handle workers in the move method
        return worker

    def __select_worker(self, position: Point2) -> Unit | None:
        """
        Same as __select_contractor, but this is used for distributing workers.
        Removes scv tag from mineral_collector_dict.
        """
        worker = next(
            (
                w
                for w in self.bot.workers.sorted(lambda x: x.distance_to(position))
                if w.tag in self.bot.mineral_collector_dict
                and not w.is_carrying_resource
            ),
            None,
        )
        if worker:
            del self.bot.mineral_collector_dict[worker.tag]
        return worker
