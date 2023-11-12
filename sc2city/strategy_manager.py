

class StrategyManager:
    def __init__(self, ai=None):
        self.opening_strategy = 3
        self.ai = ai

    def run_strategy(self):
        if self.ai.opener_manager.opener_is_active():
            self.ai.opener_manager.run_opener(opening_strategy=self.opening_strategy)
            return
        pass
