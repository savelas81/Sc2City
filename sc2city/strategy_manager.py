from opener_manager import OpenerManager


class StrategyManager:
    def __init__(self, ai=None):
        self.opening_strategy = 3
        self.ai = ai
        self.opener_manager = OpenerManager(self)

    def run_strategy(self):
        if self.opener_manager.opener_is_active():
            self.opener_manager.run_opener(opening_strategy=self.opening_strategy)
            return
        pass
