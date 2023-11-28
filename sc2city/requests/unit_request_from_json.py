# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

# UnitCreationDict:
from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM

# Typing:
import typing

# Enum:
import enum

class UnitRequestFromJson:

    def __init__(self, AI: BotAI = None):
        # Miscellaneous:
        self.AI: BotAI = AI
        self.unit_to_be_trained: typing.Optional[UnitTypeId] = None
        self.amount_to_be_trained: int = 0
        self.conditional = None
        self.target_value_dict: dict = {}


    async def queue_unit(
            self,
            conditional=None,
            ID: UnitTypeId = None,
            target_value_behaviour: bool = False,
            target_value_or_quantity_value: int = 1) -> None:
        self.conditional = conditional
        self.unit_to_be_trained = ID
        if target_value_behaviour:
            if self.unit_to_be_trained not in self.target_value_dict:
                self.target_value_dict[self.unit_to_be_trained] = target_value_or_quantity_value
                print(self.target_value_dict)
        else:
            self.amount_to_be_trained = target_value_or_quantity_value
        # facility_type_ids = UNIT_TRAINED_FROM.get(ID)
        # facility = self.AI.structures(facility_type_ids).sorted(lambda x: len(x.orders)).first
        # facility.train(ID)

    async def unit_queue_empty(self):
        if self.amount_to_be_trained <= 0:
            self.unit_to_be_trained: typing.Optional[UnitTypeId] = None
            self.amount_to_be_trained: int = 0
            self.target_value: int = 0
            self.conditional = None
            return True
        else:
            return False

    async def execute_build_units(self):
        pass
