from typing import TYPE_CHECKING

from utils import Status, OrderType
from game_objects import Order
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
    async def execute_strategy(self):
        for order in self.bot.queue:
            if order.status != Status.PENDING:
                continue

            # TODO: Handle for orders that get interrupted or take too long to start
            if not self.bot.can_afford(order.id) and not order.worker_tag:
                break

            get_next_order = False
            if order.type == OrderType.STRUCTURE:
                get_next_order = await self.scv_manager.scv_build(order)
            elif order.type == OrderType.UNIT:
                get_next_order = self.structure_manager.train_unit(order)
            elif order.type == OrderType.TECH:
                get_next_order = self.structure_manager.train_unit(order)

            if not get_next_order:
                break

        self.scv_manager.move_scvs()
