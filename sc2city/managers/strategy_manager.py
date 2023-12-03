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

    async def on_the_start(self):
        await self.AI.BuildOrderManager.on_the_start()

    async def run_strategy(self):
        await self.AI.BuildOrderManager.on_the_step()
