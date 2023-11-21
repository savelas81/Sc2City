# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId

# MapAnalyzer:
from sc2city.interfaces import MapAnalyzerInterface

# Miscellaneous:
from cache_first_frame import EnemyExpansions

# from requests import BuildRequest, UnitRequest, RequestBehaviors

# Managers:
from managers import (
    SCVManager,
    ScoutManager,
    StrategyManager,
    OpenerManager,
    MemoryManager,
    MidGameManager,
    BuildingPlacementSolver,
    CalculationManager,
    UnitRequestExecutor,
)


class Sc2City(BotAI):
    # Initialization:
    def __init__(self) -> None:
        # Configuration:
        self.raw_affects_selection = False

        # Managers:
        self.StrategyManager: StrategyManager = StrategyManager(self)

        self.CalculationManager: CalculationManager = CalculationManager(AI=self)
        self.MemoryManager: MemoryManager = MemoryManager(AI=self, debug=False)

        # Executors:
        self.UnitRequestExecutor: UnitRequestExecutor = UnitRequestExecutor(
            AI=self, debug=True
        )

        # TODO: Refactor!!!
        self.OpenerManager: OpenerManager = OpenerManager(AI=self)
        self.MidGameManager: MidGameManager = MidGameManager(self)
        self.SCVManager: SCVManager = SCVManager(AI=self)
        self.scout_manager = ScoutManager(self)
        self.enemy_expansions = EnemyExpansions(self)

        # Iteration:
        self.iteration = 0

    # Methods:
    async def on_start(self) -> None:
        # Configuration:
        self.client.game_step = 2

        # Miscellaneous:
        self.BuildingPlacementSolver: BuildingPlacementSolver = BuildingPlacementSolver(
            self
        )
        self.MapAnalyzerInterface: MapAnalyzerInterface = MapAnalyzerInterface(
            AI=self, debug=True
        )

        self.BuildingPlacementSolver.load_data()

        # Startup functions:
        await self.SCVManager.worker_split_frame_zero()
        await self.enemy_expansions.cache_enemy_expansions()

    async def on_step(self, iteration) -> None:
        self.iteration = iteration
        # Create Influence Maps:
        self.MapAnalyzerInterface.create_influence_maps()

        # Call on the managers' functions.
        self.MemoryManager.remember_units()

        await self.StrategyManager.run_strategy()
        await self.scout_manager.update_points_need_scouting()
        await self.scout_manager.move_scout()
        await self.SCVManager.move_scvs()

        # TODO: Refactor this... make it its own module.
        """
        for orbital in self.townhalls(UnitTypeId.ORBITALCOMMAND):
            if orbital.energy >= 50:
                mfs = self.mineral_field.closer_than(10, orbital)
                mf = mfs.random
                orbital(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf)
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT):
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
        """

    async def on_unit_destroyed(self, unit_tag: int):
        self.MemoryManager.forget_unit(unit_tag)
