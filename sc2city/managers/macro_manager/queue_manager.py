import copy
from typing import TYPE_CHECKING

from utils import OrderType, Status
from game_objects import Order

if TYPE_CHECKING:
    from Sc2City import Sc2City


class QueueManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def set_starting_queues(self) -> None:
        self.__sort_build_order()
        self.bot.queues = self.__distribute_queues(
            self.bot.current_strategy.build_order
        )

    def update_queues(self) -> None:
        self.__clear_finished_orders()

    def __sort_build_order(self) -> None:
        self.bot.current_strategy.build_order.sort(
            key=lambda x: x.priority, reverse=True
        )

    def __distribute_queues(
        self, merged_queue: list[Order], needs_sort=False
    ) -> dict[OrderType, list]:
        if needs_sort:
            sorted_queue = sorted(merged_queue, key=lambda x: x.priority, reverse=True)
        elif self.__is_sorted(merged_queue):
            sorted_queue = merged_queue
        else:
            sorted_queue = sorted(merged_queue, key=lambda x: x.priority, reverse=True)

        queues = {OrderType.STRUCTURE: [], OrderType.UNIT: [], OrderType.TECH: []}
        for order in sorted_queue:
            if order.target_value > 1:
                queues[order.type].extend(self.__expand_order(order))
            else:
                queues[order.type].append(order)
        return queues

    def __is_sorted(self, queue: list[Order]) -> bool:
        return all(
            current.priority >= next.priority for current, next in zip(queue, queue[1:])
        )

    def __expand_order(self, order: Order) -> list[Order]:
        new_orders = []
        for _ in range(order.target_value):
            new_order = copy.deepcopy(order)
            new_order.target_value = 1
            new_orders.append(new_order)
        return new_orders

    def __clear_finished_orders(self) -> None:
        self.bot.queues = {
            order_type: (order for order in orders if order.status != Status.FINISHED)
            for order_type, orders in self.bot.queues.items()
        }
