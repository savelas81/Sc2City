import os

from .build_order_extractor import BuildOrderExtractor

# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))
url = "https://burnysc2.github.io/sc2-planner/?&race=terran&bo=002eJyLrlbKTFGyMjHVUSqpLEhVslIqzy/KTi1SqtUhJGNoCZcpLikqTS4pLUolQpuRAV21GZKmLRYARqxXKg=="


if __name__ == "__main__":
    bo_extractor = BuildOrderExtractor(url, dir_path)
    bo_extractor.get_build_order()
