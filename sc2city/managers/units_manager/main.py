from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Sc2City import Sc2City


# TODO: Implement army logic with scripts where the army distribution is decided by the micro manager and the scripts are executed here
class UnitsManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def give_orders(self) -> None:
        pass
