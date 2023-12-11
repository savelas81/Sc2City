from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId

from utils import Status
from game_objects import BUILDING_PRIORITY, Order
from .speed_mining import SpeedMining

if TYPE_CHECKING:
    from Sc2City import Sc2City


class SCVManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.speed_mining = SpeedMining(bot)

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
        self.__speed_mining()
        self.__distribute_workers()

    # TODO: Handle for cases where the build command is not successful, since
    # the API does't return anything (maybe check if resources are being spent)
    async def scv_build(self, order: Order) -> bool:
        """
        Returns False When executing orders to avoid double commands.
        """
        if self.bot.tech_requirement_progress(order.id) != 1:
            return order.can_skip
        if order.id == UnitTypeId.REFINERY:
            await self.__build_refinery(order)
            return False
        position = await self.__get_position(order.id)
        worker = self.__select_contractor(position, order)
        # TODO: Add logic for when there are no available workers
        if not worker:
            return order.can_skip
        worker.build(order.id, position)
        order.update_status(Status.PLACEHOLDER)
        return False

    async def __get_position(self, unit_id: UnitTypeId) -> Point2:
        position_priority = BUILDING_PRIORITY[unit_id]
        possible_positions = self.bot.current_strategy.building_placements.lists[
            position_priority
        ]
        for position in possible_positions:
            if await self.bot.can_place_single(unit_id, position):
                return position
        # TODO: Handle for when all pre-defined positions are occupied
        return possible_positions[0]

    # TODO: Improve this logic
    async def __build_refinery(self, order: Order) -> None:
        for cc in self.bot.townhalls:
            geysers = self.bot.vespene_geyser.closer_than(10.0, cc)
            for geyser in geysers:
                if await self.bot.can_place_single(
                    UnitTypeId.REFINERY, geyser.position
                ):
                    worker = self.__select_contractor(cc.position, order)
                    break
            if worker:
                break
        if not worker:
            return
        worker.build(UnitTypeId.REFINERY, geyser)
        order.update_status(Status.PLACEHOLDER)

    def __speed_mining(self) -> None:
        for worker_tag in self.bot.mineral_collector_dict:
            worker = self.bot.workers.find_by_tag(worker_tag)
            mineral_tag = self.bot.mineral_collector_dict[worker_tag]
            self.speed_mining.speed_mine_minerals_single(
                worker, mineral_tag, self.bot.mineral_collector_dict
            )
        for worker_tag in self.bot.vespene_collector_dict:
            worker = self.bot.workers.find_by_tag(worker_tag)
            vespene_tag = self.bot.vespene_collector_dict[worker_tag]
            self.speed_mining.speed_mine_gas_single(
                worker, vespene_tag, self.bot.vespene_collector_dict
            )

    def __distribute_workers(self) -> None:
        self.__calculate_custom_assigned_workers()
        self.__handle_idle_workers()

    def __calculate_custom_assigned_workers(self) -> None:
        """
        Calculate custom_assigned_harvesters for CC, REFINERY and MINERALFIELD
        This is needed because we get wrong information from API when using speedmining
        """
        for structure in (
                self.bot.gas_buildings | self.bot.townhalls | self.bot.mineral_field
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
            cc.custom_surplus_harvesters = cc.custom_assigned_harvesters - (mfs_amount * 2)
        for mf in self.bot.mineral_field:
            mf.custom_surplus_harvesters = mf.custom_assigned_harvesters - 2

    def __handle_idle_workers(self) -> None:
        # TODO send scv to closest townhall that is not saturated. If not under saturated available send to closest.
        for worker in self.bot.workers:
            if worker.is_idle and worker.tag not in self.bot.contractors:
                cc = self.bot.townhalls.ready.not_flying.sorted(
                    lambda x: x.distance_to(worker)
                ).first
                mfs = self.bot.mineral_field.closer_than(10, cc)
                mf = mfs.closest_to(worker)
                self.bot.mineral_collector_dict[worker.tag] = mf.tag
                worker.gather(mf)

    def __assign_worker_to_mineral_field(
        self, worker: Unit, mineral_field: Unit
    ) -> None:
        worker.gather(mineral_field)
        self.bot.mineral_collector_dict[worker.tag] = mineral_field.tag

    # TODO: Handle scv assigned task so that the same one is not called for more than one task
    def __select_contractor(self, position: Point2, order: Order) -> Unit | None:
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
            order.worker_tag = worker.tag
        return worker
