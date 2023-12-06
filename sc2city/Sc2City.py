from sc2.bot_ai import BotAI
from sc2.data import Race

from history_analyzer import HistoryAnalyzer
from map_analyzer import MapAnalyzer
from macro_manager import MacroManager
from micro_manager import MicroManager
from build_order_manager import BuildOrderManager
from units_manager import UnitsManager


class Sc2City(BotAI):
    race = Race.Terran

    def __init__(self):
        self.current_strategy = None
        self.history_analyzer = HistoryAnalyzer()
        self.map_analyzer = MapAnalyzer(self)
        self.macro_manager = MacroManager(self)
        self.micro_manager = MicroManager()
        self.build_order_manager = BuildOrderManager(self)
        self.units_manager = UnitsManager()

    async def on_start(self) -> None:
        self.client.game_step = 2
        self.macro_manager.choose_first_strategy()
        self.build_order_manager.execute_frame_zero()
        await self.map_analyzer.get_expansions()

    async def on_step(self, iteration) -> None:
        pass
