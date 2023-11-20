import random
from sc2.player import Computer
from sc2.data import Race
from sc2 import maps
from sc2.main import *
from sc2.data import Difficulty
from sc2city.managers.allocators.building_placements import BuildingPlacementSolver


class BuildingPlacementDebugger(BotAI):
    def __init__(self):
        self.placement_solver = BuildingPlacementSolver(self)

    async def on_start(self):
        self.placement_solver.load_data()

    async def on_step(self, iteration):
        self.placement_solver.draw_debug()


def main():
    mapname = "DragonScalesAIE"
    opponents = [Race.Protoss, Race.Zerg, Race.Terran]
    opponent = random.choice(opponents)
    # opponent = Race.Terran

    run_game(
        maps.get(mapname),
        [
            Bot(Race.Terran, BuildingPlacementDebugger()),
            Computer(opponent, Difficulty.VeryHard),
        ],
        realtime=False,
        save_replay_as="replay.SC2Replay",
    )


if __name__ == "__main__":
    main()
