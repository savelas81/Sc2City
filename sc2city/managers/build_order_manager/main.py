from typing import TYPE_CHECKING

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

    async def execute_strategy(self):
        await self.scv_manager.move_scvs()
        self.structure_manager.execute_builds()
