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
            BuildRequest(
                ID=UnitTypeId.FACTORY,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """
            # 1:03 Set amount of gas miners worldwide to 3     
            # 1:12 Set amount of gas miners worldwide to 6
            """
            """BuildRequest(
                ID=UnitTypeId.ORBITALCOMMAND,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            BuildRequest(
                ID=UnitTypeId.BARRACKSTECHLAB,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
                """
                # Make the AI build the factory near this techlab instead of the normal prioritization
                """
            ),
             """
             # Lift the barracks off to build another techlab. Make sure to don't block the future factory landing!
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
            """
            # Lift and land the factory on the available techlab
            """
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.SIEGETANK,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
            ),
            """UpgradeRequest(
                ID=UnitTypeId.STIMPACK,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARINE,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=4
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKS,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
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
                ID=UnitTypeId.BARRACKSREACTOR,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARINE,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=12
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=2,
            ),
            """UpgradeRequest(
                ID=UnitTypeId.SHIELDWALL,
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
                ID=UnitTypeId.MARINE,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=8
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKSREACTOR,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARINE,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
                """
                # Set the marine to be secondairy to the siege tanks!
                """
            ),
        """
        # Queue up a high priority supply depot every time supply gets 8 supply before the limit
        """
        ]