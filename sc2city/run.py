import sys

from __init__ import run_ladder_game

# Load bot
from Sc2City import Sc2City

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer


bot = Bot(Race.Terran, Sc2City())

# Start game
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponentid = run_ladder_game(bot)
        print(result, " against opponent ", opponentid)
    else:
        # Local game
        print("Starting local game...")
        run_game(maps.get("DragonScalesAIE"),
                 [bot, Computer(Race.Protoss, Difficulty.VeryHard)],
                 realtime=False,
                 save_replay_as="replay.SC2Replay")



