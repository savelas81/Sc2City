from typing import TYPE_CHECKING

from game_objects import Order

if TYPE_CHECKING:
    from Sc2City import Sc2City


class QueueManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def set_starting_queues(self) -> None:
        queue = self.bot.current_strategy.build_order

    def update_queues(self) -> None:
        pass
