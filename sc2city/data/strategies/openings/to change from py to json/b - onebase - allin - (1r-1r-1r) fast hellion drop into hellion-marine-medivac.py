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
                ID=UnitTypeId.REFINERY,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=2,
            ),
            """
            # 0:47 Set amount of gas miners worldwide to 3
            """
            BuildRequest(
                ID=UnitTypeId.BARRACKS,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """  
            # 0:53 Set amount of gas miners worldwide to 6
            """
            BuildRequest(
                ID=UnitTypeId.BARRACKSREACTOR,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            BuildRequest(
                ID=UnitTypeId.FACTORY,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """
            # Place the factory near the barrack that's building the reactor
            """
            """BuildRequest(
                ID=UnitTypeId.ORBITALCOMMAND,
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
            """
            # Lift up the barracks and start building the upcoming reactor
            # Place the factory at the available reactor
            """
            BuildRequest(
                ID=UnitTypeId.STARPORT,
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
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """
            # Lift up the barracks and land the barracks so the upcoming reactor can be build
            """
            BuildRequest(
                ID=UnitTypeId.BARRACKSREACTOR,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
            """
            # Lift the starport and place it at the available reactor
            """
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MEDIVAC,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=2,
            ),
            UnitRequest(
                conditional=None,
                AI=self.AI,
                ID=UnitTypeId.MARINE,
                target_value_or_quantity_value_behavior=RequestBehaviors.TARGET_BEHAVIOR,
                target_value_or_quantity_value=1500
            ),
            BuildRequest(
                ID=UnitTypeId.SUPPLYDEPOT,
                AI=self.AI,
                target_value_or_quantity_value=RequestBehaviors.QUANTITY_BEHAVIOR,
                target_value_or_quantity_value=1,
            ),
        """
        # Queue up a high priority supply depot every time supply gets 8 supply before the limit
        """
        ]