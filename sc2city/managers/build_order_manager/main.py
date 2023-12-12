import asyncio
from typing import TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit

from utils import Status, OrderType, SCVAssignment
from .scv_manager import SCVManager
from .structure_manager import StructureManager

if TYPE_CHECKING:
    from Sc2City import Sc2City


class BuildOrderManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.scv_manager = SCVManager(bot)
        self.structure_manager = StructureManager(bot)
        self.order_managers = {
            OrderType.STRUCTURE: self.scv_manager.scv_build,
            OrderType.PRODUCTION: self.structure_manager.produce,
            OrderType.ACTION: self.structure_manager.execute_action,
            OrderType.SCV_ACTION: self.scv_manager.execute_action,
        }

    def execute_frame_zero(self) -> None:
        self.scv_manager.worker_split_frame_zero()

    async def execute_strategy(self) -> None:
        await self.__execute_next_order()
        self.scv_manager.move_scvs()
        self.structure_manager.handle_supply_depots()

    def production_complete(self, unit: Unit) -> None:
        order = next(
            (
                order
                for order in self.bot.queue
                if order.id == unit.type_id and order.status == Status.STARTED
            ),
            None,
        )
        if order is not None:
            order.update_status(Status.FINISHED)
            if order.type == OrderType.STRUCTURE:
                self.bot.scvs[SCVAssignment.BUILD].remove(order.tag)
                if (
                    order.id == UnitTypeId.REFINERY
                ):  # worker goes automatically to gather gas.
                    self.bot.scvs[SCVAssignment.VESPENE][order.tag] = unit.tag
        else:
            # TODO: Add logic to handle errors
            print(f"{unit.type_id} not found in finished queue")

    def building_construction_started(self, unit: Unit) -> None:
        order = next(
            (
                order
                for order in self.bot.queue
                if order.id == unit.type_id and order.status == Status.PENDING
            ),
            None,
        )
        if order is not None:
            order.update_status(Status.STARTED)
        else:
            # TODO: Add logic to handle errors
            print(f"{unit.type_id} not found in starting queue")

    # TODO: Implement logic for conditional orders
    async def __execute_next_order(self) -> None:
        for order in self.bot.queue:
            order.get_old(self.bot.client.game_step)
            if order.status != Status.PENDING:
                continue

            manager = self.order_managers[order.type]
            get_next_order = (
                await manager(order)
                if asyncio.iscoroutinefunction(manager)
                else manager(order)
            )
            if not get_next_order:
                break
