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
    current_strategy = None

    def __init__(self):
        self.history_analyzer = HistoryAnalyzer()
        self.map_analyzer = MapAnalyzer()
        self.macro_manager = MacroManager(self)
        self.micro_manager = MicroManager()
        self.build_order_manager = BuildOrderManager()
        self.units_manager = UnitsManager()

    async def on_start(self):
        self.client.game_step = 2
        self.macro_manager.choose_first_strategy()

    async def on_step(self, iteration):
        pass
