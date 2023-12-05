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
        self.send_first_scv_scout = True

    async def on_the_start(self):
        await self.AI.BuildOrderManager.on_the_start()

    async def run_strategy(self):
        if self.send_first_scv_scout and self.AI.time >= 37:
            scouting_scv = await self.AI.SCVManager.select_contractor(position=self.AI.start_location)
            await self.AI.scout_manager.assign_unit_tag_scout(scouting_scv.tag)
            await self.AI.scout_manager.create_scouting_grid_for_enemy_main()
            self.send_first_scv_scout = False
            return
        if await self.AI.BuildOrderManager.build_order_list_empty():
            print("build order completed")
        else:
            await self.AI.BuildOrderManager.on_the_step()
