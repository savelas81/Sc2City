# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# Classes:

"""
TODO: Documentation here..
"""

class StrategyManager:
    def __init__(self, AI: BotAI = None):
        # Miscellaneous:
        self.AI: BotAI = AI

        # Integers:
        self.opening_strategy: int = 1

    async def run_strategy(self):
        if self.AI.OpenerManager.manager_is_active:
            await self.AI.OpenerManager.run_opener(
                opening_strategy=self.opening_strategy
            )

            return
        if self.AI.MidGameManager.manager_is_active:
            await self.AI.MidGameManager.run_manager()
        else:
            # TODO end game stuff
            pass
