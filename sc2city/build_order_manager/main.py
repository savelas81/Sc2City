import json
import loguru

from sc2.bot_ai import BotAI
from utils import MapTypes
from .scv_manager import SCVManager


class BuildOrderManager:
    def __init__(self, bot: BotAI):
        self.bot = bot
        self.map_file = None
        self.building_placements = None
        self.scv_manager = SCVManager(bot)

    def execute_frame_zero(self):
        self.__set_map_filename()
        self.__update_building_placements()
        self.scv_manager.worker_split_frame_zero()

    def __update_building_placements(self):
        if not self.bot.current_strategy.get("build_type"):
            loguru.logger.info(f"Not able to find build_type")
            return None

        build_type = self.bot.current_strategy.get("build_type")
        map_path = getattr(MapTypes, build_type).value
        full_path = map_path + self.map_file
        self.building_placements = self.__load_building_placements(full_path)

    def __load_building_placements(self, buildings_file: str):
        try:
            with open(buildings_file, "r") as f:
                building_placements = json.load(f)
            return building_placements
        except (OSError, IOError) as e:
            print("Building placement file not found.")
            print(e)

    def __set_map_filename(self):
        # This function should only run at the start of the game to discover the correct set of map files
        map_name = self.bot.game_info.map_name
        starting_location = self.bot.start_location
        self.map_file = map_name + str(starting_location) + ".json"
