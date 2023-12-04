# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# Typing:
import typing

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId


class StructureQueueManager:
    def __init__(self, AI: BotAI = None, debug: bool = False):
        # Miscellaneous:
        self.AI: BotAI = AI
        self.structure_to_be_build: typing.Optional[UnitTypeId] = None
        self.amount_to_be_build: int = 0
        self.conditional = None
        self.target_value_dict: dict = {}

    async def queue_building(
        self,
        conditional=None,
        ID: UnitTypeId = None,
        target_value_behaviour: bool = False,
        target_value_or_quantity_value: int = 1,
    ) -> None:
        """
        queue_building is used to queue next building.

        """
        self.conditional = conditional
        self.structure_to_be_build = ID
        if target_value_behaviour:
            if self.structure_to_be_build not in self.target_value_dict:
                self.target_value_dict[
                    self.structure_to_be_build
                ] = target_value_or_quantity_value
                print(self.target_value_dict)
        else:
            self.amount_to_be_build = target_value_or_quantity_value

    async def structure_queue_empty(self) -> bool:
        """
        checks if the structure production queue is empty.
        If queue is empty return true.
        Clears variables related to structure queue if queue is empty.
        """
        if self.amount_to_be_build <= 0:
            self.amount_to_be_build: typing.Optional[UnitTypeId] = None
            self.amount_to_be_build: int = 0
            self.conditional = None
            return True
        else:
            return False

    async def execute_build_structures(self):
        if not self.AI.SCVManager.building_queue_empty:
            return
        if self.structure_to_be_build and self.amount_to_be_build > 0:
            if not self.we_can_build_next_building():
                return
            await self.AI.SCVManager.queue_building(self.structure_to_be_build)
            self.amount_to_be_build -= 1

    def we_can_build_next_building(self) -> bool:
        next_to_be_build = self.structure_to_be_build
        if next_to_be_build == UnitTypeId.SUPPLYDEPOT:
            if self.AI.minerals > 30:
                return True
            return False
        if next_to_be_build in [UnitTypeId.BARRACKS, UnitTypeId.ENGINEERINGBAY]:
            if (
                self.AI.minerals > 60
                and self.AI.structures(
                    [UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED]
                ).ready
            ):
                return True
            return False
        if next_to_be_build in [UnitTypeId.ARMORY]:
            if (
                self.AI.minerals > 60
                and self.AI.vespene > 60
                and self.AI.structures([UnitTypeId.FACTORY]).ready
            ):
                return True
            return False
        if next_to_be_build in [UnitTypeId.SENSORTOWER, UnitTypeId.MISSILETURRET]:
            if (
                self.AI.minerals > 50
                and self.AI.structures([UnitTypeId.ENGINEERINGBAY]).ready
            ):
                return True
            return False
        if next_to_be_build == UnitTypeId.FACTORY:
            if (
                self.AI.minerals > 60
                and self.AI.vespene > 60
                and (
                    self.AI.structures(UnitTypeId.BARRACKS).ready
                    or self.AI.structures(UnitTypeId.BARRACKSFLYING)
                )
            ):
                return True
            return False
        if next_to_be_build == UnitTypeId.GHOSTACADEMY:
            if self.AI.minerals > 60 and (
                self.AI.structures(UnitTypeId.BARRACKS).ready
                or self.AI.structures(UnitTypeId.BARRACKSFLYING)
            ):
                return True
            return False
        if next_to_be_build == UnitTypeId.FUSIONCORE:
            if (
                self.AI.minerals > 60
                and self.AI.vespene > 100
                and (
                    self.AI.structures(UnitTypeId.STARPORT).ready
                    or self.AI.structures(UnitTypeId.STARPORTFLYING)
                )
            ):
                return True
            return False
        if next_to_be_build == UnitTypeId.BUNKER:
            if self.AI.minerals > 50 and (
                self.AI.structures(UnitTypeId.BARRACKS).ready
                or self.AI.structures(UnitTypeId.BARRACKSFLYING)
            ):
                return True
            return False
        if next_to_be_build == UnitTypeId.STARPORT:
            if (
                self.AI.minerals > 60
                and self.AI.vespene > 60
                and (
                    self.AI.structures(
                        [UnitTypeId.FACTORY, UnitTypeId.FACTORYFLYING]
                    ).ready
                    or self.AI.structures(UnitTypeId.BARRACKSFLYING)
                )
            ):
                return True
            return False
        if next_to_be_build == UnitTypeId.REFINERY:
            return True
        if next_to_be_build == UnitTypeId.COMMANDCENTER:
            if self.AI.minerals > 250:
                return True
            return False
        print("Structure_queue_manager: Unknown " + str(next_to_be_build))
