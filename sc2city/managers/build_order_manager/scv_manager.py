from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId

from utils import Status, OrderType
from game_objects import BUILDING_PRIORITY

if TYPE_CHECKING:
    from Sc2City import Sc2City


class SCVManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

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

    async def move_scvs(self) -> None:
        self.__efficient_mining()
        self.__distribute_workers()
        await self.__build_structures()

    def __efficient_mining(self) -> None:
        pass

    def __distribute_workers(self) -> None:
        pass

    # TODO: Improve logic and refactor
    # TODO: Implement logic for conditional orders
    # TODO: Handle for when SCV's have the order, but haven't started building
    async def __build_structures(self) -> None:
        for order in self.bot.queues[OrderType.STRUCTURE]:
            if order.status != Status.PENDING:
                continue
            if not self.bot.can_afford(order.id):
                return
            if order.id == UnitTypeId.REFINERY:
                position = self.__build_refinery(order)
                return
            position = await self.__get_position(order.id)
            worker = self.__select_contractor(position)
            # TODO: Add logic for when there are no available workers
            if not worker:
                return
            worker.build(order.id, position)

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
    def __build_refinery(self) -> None:
        for cc in self.bot.townhalls:
            geysers = self.bot.vespene_geyser.closer_than(10.0, cc)
            for geyser in geysers:
                if self.bot.can_place(UnitTypeId.REFINERY, geyser):
                    worker = self.__select_contractor(cc.position)
                    break
            if worker:
                break
        if not worker:
            return
        worker.build(UnitTypeId.REFINERY, geyser)

    def __assign_worker_to_mineral_field(
        self, worker: Unit, mineral_field: Unit
    ) -> None:
        worker.gather(mineral_field)
        self.bot.mineral_collector_dict[worker.tag] = mineral_field.tag

    # TODO: Handle scv assigned task so that the same one is not called for more than one task
    def __select_contractor(self, position: Point2) -> Unit | None:
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
        return worker
