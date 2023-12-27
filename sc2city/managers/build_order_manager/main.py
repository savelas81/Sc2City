import asyncio
from typing import TYPE_CHECKING

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit

from utils import OrderType, SCVAssignment, Status

from .scv_manager import SCVManager
from .structure_manager import StructureManager

if TYPE_CHECKING:
    from Sc2City import Sc2City


class BuildOrderManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.scv_manager = SCVManager(bot)
        self.structure_manager = StructureManager(bot)
        self.__order_managers = {
            OrderType.STRUCTURE: self.scv_manager.scv_build,
            OrderType.PRODUCTION: self.structure_manager.produce,
            OrderType.ACTION: self.structure_manager.execute_action,
            OrderType.SCV_ACTION: self.scv_manager.execute_action,
        }

    def execute_frame_zero(self) -> None:
        self.scv_manager.worker_split_frame_zero()
        townhall = self.bot.townhalls.first
        self.bot.bases[townhall.position].add_townhall(townhall.tag)

    async def execute_strategy(self) -> None:
        await self.__execute_next_order()
        self.scv_manager.move_scvs()
        self.structure_manager.handle_supply_depots()

    def production_complete(self, unit: Unit) -> None:
        order_id = (
            AbilityId.CALLDOWNMULE_CALLDOWNMULE
            if unit.type_id == UnitTypeId.MULE
            else unit.type_id
        )
        order = next(
            (
                order
                for order in self.bot.queue
                if order.id == order_id and order.status == Status.STARTED
            ),
            None,
        )
        if not order:
            # TODO: Add logic to handle errors
            print(f"{unit.type_id} not found in finished queue")
            return

        order.update_status(Status.FINISHED)
        if unit.is_collecting:
            unit.stop()  # Only SCVManager can give collection orders

        if order.type != OrderType.STRUCTURE:
            return

        new_assignment = (
            SCVAssignment.VESPENE  # worker goes automatically to gather gas.
            if order_id == UnitTypeId.REFINERY
            else SCVAssignment.NONE
        )
        resource = unit if order_id == UnitTypeId.REFINERY else None
        self.scv_manager.update_worker_assignment(
            order.tag, SCVAssignment.BUILD, new_assignment, resource
        )

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

            manager = self.__order_managers[order.type]
            get_next_order = (
                await manager(order)
                if asyncio.iscoroutinefunction(manager)
                else manager(order)
            )
            if not get_next_order:
                break
