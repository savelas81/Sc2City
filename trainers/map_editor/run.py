import os
import sys

if __name__ == "__main__":
    # Get the absolute path of the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Add the relative path for the bot script to sys.path
    main_bot_path = os.path.abspath(os.path.join(dir_path, "..", "..", "sc2city"))
    sys.path.append(main_bot_path)

from sc2.data import Difficulty, Race
from sc2.player import Bot, Computer

from sc2city.utils import BuildTypes, Game
from trainers.map_editor.config import MapType
from trainers.map_editor.placement_extractor import BuildingPlacementExtractor


def setup_and_start_game(
    map_name: str, map_type: MapType, build_type: BuildTypes
) -> bool:
    bot = BuildingPlacementExtractor(main_bot_path, map_type, build_type)
    player = Bot(bot.race, bot)
    opponent = Computer(Race.Protoss, Difficulty.Easy)

    game = Game(map_name, player, opponent, realtime=False)
    game.start()
    return bot.map_pins_saved


def main(map_name: str, map_type: MapType, build_type: BuildTypes) -> None:
    # TODO: Add logic to handle multiple maps
    map_pins_saved = False

    # TODO: Add map type and build type to filenames allowing to run multiple maps at once
    while not map_pins_saved:
        print("Starting game...")
        map_pins_saved = setup_and_start_game(map_name, map_type, build_type)


if __name__ == "__main__":
    map_name = "DragonScalesAIE-A-Player_2"
    map_type = MapType.ONE_SIDE
    build_type = BuildTypes.ONE_BASE
    main(map_name, map_type, build_type)
