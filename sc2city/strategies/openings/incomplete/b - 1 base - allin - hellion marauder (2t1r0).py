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
                target_value_or_quantity_value=22
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
                ID=UnitTypeId.REFINERY,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=2,
            ),
            """
            # 1:03 Set amount of gas miners worldwide to 3     
            # 1:12 Set amount of gas miners worldwide to 4
            """
            """BuildRequest(
                ID=UnitTypeId.ORBITALCOMMAND,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            BuildRequest(
                ID=UnitTypeId.FACTORY,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
                """
                # Make it prioritize being next to the barracks over the prioritisation locations
                """
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKSREACTOR,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """
            # Lift the barrack and build the upcoming techlab somewhere close (don't include priority locations, this one can go anywhere
            # When done, lift the factory and place it on the reactor that the barrack build
            """
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKSTECHLAB,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.HELLION,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKS,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARAUDER,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1
            ),
            """
            # 2:44 Set amount of gas miners worldwide to 3
            """
            """BuildRequest(
                ID=UpgradeId.STIMPACK,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARAUDER,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKSTECHLAB,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARAUDER,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARAUDER,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARAUDER,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=3
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """BuildRequest(
                ID=UpgradeId.CONCUSSIONSHELLS,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARAUDER,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
                """
                # Set the prioritisation of the marauders above the hellions now.
                """
            ),
        ]