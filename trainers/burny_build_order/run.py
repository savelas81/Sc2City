import os
import sys

# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))
# Add the relative path for the bot script to sys.path
main_bot_path = os.path.abspath(os.path.join(dir_path, "..", "..", "sc2city"))
sys.path.append(main_bot_path)

from build_order_extractor import BuildOrderExtractor
from sc2city.utils import BuildTypes

url = """
https://burnysc2.github.io/sc2-planner/?&race=terran&bo=002eJy9UksKwjAUvMtbd9EkrY29irgobZAgtCUmiIh3d9cI9o1NkG4zzLz55PQkO1Bb1QX5x2yopfvkrsbRq/iFiOOC3LwLvQ/ObKDJEtAgqBas672dxi3H9qEIFAmBOb0DJC4SRuvjUkoCD3hHRlI2gNRwFeIumFM5TShkD4KwDQWr0kz70WWYL64bPvTUOkVp5PDA6nEWWGsoD7ti6hUuZapOVoparJO493+F26fa1HSiYf+OrNDfLjnH+gs4vwFKk/0A
"""
build_type = BuildTypes.ONE_BASE

if __name__ == "__main__":
    bo_extractor = BuildOrderExtractor(url, build_type, dir_path)
    bo_extractor.get_build_order()
