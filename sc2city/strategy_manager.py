class StrategyManager:
    def __init__(self, ai=None):
        self.opening_strategy = 1
        self.ai = ai

    async def run_strategy(self):
        if self.ai.opener_manager.manager_is_active():
            await self.ai.opener_manager.run_opener(
                opening_strategy=self.opening_strategy
            )
            return
        if self.ai.mid_game_manager.manager_is_active():
            await self.ai.mid_game_manager.run_manager()
        else:
            # TODO end game stuff
            pass
