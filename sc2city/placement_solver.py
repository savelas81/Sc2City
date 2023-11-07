from sc2.bot_ai import BotAI
import random
from sc2.player import Bot, Computer
from sc2.data import Race
from sc2 import maps
from sc2.main import *
from sc2.data import Difficulty
from building_placements import BuildingPlacementSolver
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId
from sc2.units import Units
from sc2.position import Point2, Point3


class BuildingPlacementExtractor(BotAI):

    def __init__(self):
        self.placement_solver = BuildingPlacementSolver(self)

    async def on_start(self):
        pass

    async def on_step(self, iteration):
        cc = self.structures(UnitTypeId.COMMANDCENTER).first
        rax = self.structures(UnitTypeId.BARRACKS).closest_to(self.start_location)
        # print(rax.distance_to(cc))
        if rax.distance_to(cc) > 30:
            pass
        elif iteration == 30:
            self.placement_solver.save_placements(buildings=self.structures)


def main():
    mapname = "TEST"
    opponents = [Race.Protoss, Race.Zerg, Race.Terran]
    opponent = random.choice(opponents)
    # opponent = Race.Terran

    run_game(
        maps.get(mapname),
        [Bot(Race.Terran, BuildingPlacementExtractor()), Computer(opponent, Difficulty.VeryHard)],
        realtime=False,
        save_replay_as="replay.SC2Replay",
    )


if __name__ == '__main__':
    main()
