from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Sc2City import Sc2City


class UnitQueue:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
