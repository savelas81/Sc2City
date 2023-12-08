import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Sc2City import Sc2City


class QueueManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def set_starting_queues(self) -> None:
        self.bot.current_strategy.build_order.sort(
            key=lambda x: x.priority, reverse=True
        )
        for order in self.bot.current_strategy.build_order:
            if order.target_value > 1:
                for _ in range(order.target_value):
                    copy_order = copy.deepcopy(order)
                    copy_order.target_value = 1
                    self.bot.queues[order.type].append(copy_order)
            else:
                self.bot.queues[order.type].append(order)

        print(self.bot.queues)

    def update_queues(self) -> None:
        pass
