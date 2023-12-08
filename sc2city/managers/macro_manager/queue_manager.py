from typing import TYPE_CHECKING

from utils import OrderType

if TYPE_CHECKING:
    from Sc2City import Sc2City


class QueueManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def set_starting_queues(self) -> None:
        structure_queue = [
            order
            for order in self.bot.current_strategy.build_order
            if order.type == OrderType.STRUCTURE
        ]
        unit_queue = [
            order
            for order in self.bot.current_strategy.build_order
            if order.type == OrderType.UNIT
        ]
        tech_queue = [
            order
            for order in self.bot.current_strategy.build_order
            if order.type == OrderType.TECH
        ]

    def update_queues(self) -> None:
        pass
