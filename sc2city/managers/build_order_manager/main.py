from typing import TYPE_CHECKING

from sc2.unit import Unit

from utils import Status, OrderType
from .scv_manager import SCVManager
from .structure_manager import StructureManager

if TYPE_CHECKING:
    from Sc2City import Sc2City


class BuildOrderManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.scv_manager = SCVManager(bot)
        self.structure_manager = StructureManager(bot)

    def execute_frame_zero(self) -> None:
        self.scv_manager.worker_split_frame_zero()

    # TODO: Implement logic for conditional orders
    async def execute_strategy(self) -> None:
        for order in self.bot.queue:
            order.get_old(self.bot.client.game_step)
            if order.status != Status.PENDING:
                continue
            if not self.bot.can_afford(order.id):
                break

            get_next_order = order.can_skip  # Maybe redundant
            if order.type == OrderType.STRUCTURE:
                get_next_order = await self.scv_manager.scv_build(order)
            elif order.type == OrderType.UNIT:
                get_next_order = self.structure_manager.train_unit(order)
            elif order.type == OrderType.TECH:
                get_next_order = self.structure_manager.upgrade(order)

            if not get_next_order:
                break

        self.scv_manager.move_scvs()

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
                self.bot.contractors.remove(order.worker_tag)
        else:
            # TODO: Add logic to handle errors
            print(f"{unit.type_id} not found in finished queue")

    def building_construction_started(self, unit: Unit) -> None:
        order = next(
            (
                order
                for order in self.bot.queue
                if order.id == unit.type_id and order.status == Status.PLACEHOLDER
            ),
            None,
        )
        if order is not None:
            order.update_status(Status.STARTED)
        else:
            # TODO: Add logic to handle errors
            print(f"{unit.type_id} not found in starting queue")
