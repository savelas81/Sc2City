from sc2city.requests import RequestBehaviors, UnitRequest
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
import typing

class FourRaxAllInSequence:
    def __init__(self, AI: BotAI):
        self.AI: BotAI = AI

    def sequence(self) -> typing.List[typing.Any]:
        return [
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.SCV,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=8
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKS,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            BuildRequest(
                ID=UnitTypeId.COMMANDCENTER,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=2,
            ),
            """BuildRequest(
                ID=UnitTypeId.ORBITALCOMMAND,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            """
            # If the scouting information allows a midgame, choose a midgame from the folder: barrack, command, orbital, command
            # if the scouting information is 1 base play, cancel the second build command center and choose a midgame from the folder: phase_3
            """
            """
            https://burnysc2.github.io/sc2-planner/?&race=terran&settings=tLuDriterisSritnjUrisEritm2KsLuFsExSGtZWxRGsKIGOuFtN&optimizeSettings=tLuDriterisSritTrisEritmxIEtRccPUfnePdlcVrjsKUVIMSINriuFsExoGtdnsKxqGsIuFtN&bo=002eJyLrlbKTFGyMjHVUSqpLEhVslIqzy/KTi1SqtUhJGNoCZcpLikqTS4pLUolQpuRIVnayHKhBVlWGRob4dGH11BzuFxicklmfh4+22IBiy549g==
            """
        ]