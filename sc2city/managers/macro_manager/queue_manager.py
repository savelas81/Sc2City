import copy
from typing import TYPE_CHECKING

from utils import Status
from game_objects import Order

if TYPE_CHECKING:
    from Sc2City import Sc2City


class QueueManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def start_new_queue(self, orders: list[Order]) -> None:
        self.bot.queue.clear()
        for order in orders:
            if order.target_value > 1:
                self.bot.queue.extend(self.__expand_order(order))
            else:
                self.bot.queue.append(order)
        self.bot.queue.sort(key=lambda x: x.priority, reverse=True)

    def update_queue(self) -> None:
        self.__clear_finished_orders()

    def __expand_order(self, order: Order) -> list[Order]:
        new_orders = []
        for _ in range(order.target_value):
            new_order = copy.deepcopy(order)
            new_order.target_value = 1
            new_orders.append(new_order)
        return new_orders

    def __clear_finished_orders(self) -> None:
        self.bot.queue = [
            order for order in self.bot.queue if order.status != Status.FINISHED
        ]
