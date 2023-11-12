

class StrategyManager:
    def __init__(self, ai=None):
        self.opening_strategy = 3
        self.ai = ai

    async def run_strategy(self):
        if self.ai.opener_manager.opener_is_active():
            await self.ai.opener_manager.run_opener(opening_strategy=self.opening_strategy)
            return
        else:
            # TODO make mid and end game stuff
            pass
