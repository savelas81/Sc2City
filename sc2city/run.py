import sys

from sc2.data import Difficulty, Race
from sc2.player import Bot, Computer

from Sc2City import Sc2City
from utils import Game, Settings

# Start game
if __name__ == "__main__":
    bot = Sc2City(Settings.from_json_file())
    player = Bot(bot.race, bot)
    opponent = Computer(Race.Protoss, Difficulty.VeryHard)
    map = "DragonScalesAIE"

    if "--LadderServer" in sys.argv:
        game = Game(map, player)
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponent_id = game.run_ladder_game()
        print(result, " against opponent ", opponent_id)
    else:
        game = Game(map, player, opponent)
        # Local game
        print("Starting local game...")
        game.start()
