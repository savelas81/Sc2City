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
            """
            # 0:47 Set amount of gas miners worldwide to 3     
            # 0:53 Set amount of gas miners worldwide to 6
            """
            BuildRequest(
                ID=UnitTypeId.REFINERY,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=2,
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKS,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
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
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKS,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKSTECHLAB,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            )
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """
            # Lift the barracks and factory up. Put the factory down at the available techlab
            # Land the barracks in preparation of building the future techlab
            """
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.SIEGETANK,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
            ),
            BuildRequest(
                ID=UnitTypeId.BARRACKSTECHLAB,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=2,
            )
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
            """UpgradeRequest(
                ID=UnitTypeId.STIMPACK,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            """UpgradeRequest(
                ID=UnitTypeId.CONCUSSIONSHELL,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARINE,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=3
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """UpgradeRequest(
                ID=UnitTypeId.SHIELDWALL,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),"""
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARAUDER,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=3
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
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARINE,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARAUDER,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
            ),
            """
            # Would it be possible for the bot to calculate for itself how much resources it has in the future with the current BO?
            # In that case we would prioritize Tank>Marauder>Marine, but the build is not gas stable.
            # If the second queue doesn't have enough gas for a marauder, queue a marine (without stagnating tank production)
            """
        """
        # Queue up a high priority supply depot every time supply gets 8 supply before the limit
        """
        ]