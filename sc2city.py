# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > Player:
from sc2.player import Computer, Bot

# > Main:
from sc2.main import run_game

# > Data:
from sc2.data import Difficulty, Race

# > Maps:
from sc2 import maps

# Modules:

from managers import (
    CalculationManager,
    MemoryManager,

    UnitRequestExecutor,
)

# Classes:
class SC2City(BotAI):
    # Initialization:
    def __init__(self) -> None:
        # Configuration:
        self.raw_affects_selection = False

        # Integers:
        self.iteration: int = 0

    # Methods:
    async def on_start(self) -> None:
        # Configuration:
        self.client.game_step = 8

        # Managers:
        self.CalculationManager: CalculationManager = CalculationManager(AI=self)
        self.MemoryManager: MemoryManager = MemoryManager(AI=self, debug=True)

        self.UnitRequestExecutor: UnitRequestExecutor = UnitRequestExecutor(AI=self)

    async def on_step(self, iteration: int) -> None:
        self.MemoryManager.remember_units()
        self.UnitRequestExecutor.on_step()

    # Events:
    async def on_unit_destroyed(self, unit_tag: int) -> None:
        self.MemoryManager.forget_unit(unit_tag)


# Main:


if __name__ == "__main__":
    run_game(
        map_settings=maps.get("DragonScalesAIE"),
        players=[
            Bot(Race.Terran, SC2City()),
            Computer(Race.Protoss, Difficulty.VeryHard),
        ],
        realtime=True,
        save_replay_as="replay.SC2Replay",
    )
