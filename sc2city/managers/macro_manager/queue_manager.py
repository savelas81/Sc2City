import copy
from typing import TYPE_CHECKING

from game_objects import Order, CustomOrders

if TYPE_CHECKING:
    from Sc2City import Sc2City


class QueueManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def start_new_queue(self, orders: list[Order]) -> None:
        self.bot.queue.clear()
        for order in orders:
            if order.id in CustomOrders:
                self.__handle_custom_order(order)
            if order.quantity > 1:
                self.bot.queue.extend(self.__expand_order(order))
            else:
                self.bot.queue.append(order)
        self.__sort_queue()

    def update_queue(self) -> None:
        self.__sort_queue()

    def __handle_custom_order(self, order: Order) -> None:
        pass

    def __expand_order(self, order: Order) -> list[Order]:
        new_orders = []
        for _ in range(order.quantity):
            new_order = copy.deepcopy(order)
            new_order.quantity = 1
            new_orders.append(new_order)
        return new_orders

    def __sort_queue(self) -> None:
        self.bot.queue.sort(key=lambda x: x.priority, reverse=True)
