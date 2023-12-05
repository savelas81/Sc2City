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
        self.history_analyzer = HistoryAnalyzer()
        self.map_analyzer = MapAnalyzer()
        self.macro_manager = MacroManager()
        self.micro_manager = MicroManager()
        self.build_order_manager = BuildOrderManager()
        self.units_manager = UnitsManager()

    async def on_start(self):
        self.client.game_step = 2
