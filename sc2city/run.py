import sys

from sc2.data import Difficulty, Race
from sc2.player import Bot, Computer

# Load game client and bot
from util.game import Game
from Sc2City import Sc2City

# Start game
if __name__ == "__main__":
    bot = Bot(Race.Terran, Sc2City())
    opponent = Computer(Race.Protoss, Difficulty.VeryHard)
    map = "DragonScalesAIE"

    if "--LadderServer" in sys.argv:
        game = Game(map, bot)
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponentid = game.run_ladder_game()
        print(result, " against opponent ", opponentid)
    else:
        game = Game(map, bot, opponent)
        # Local game
        print("Starting local game...")
        game.start()
