# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

# Typing:
import typing

# Requests:
from .request import RequestBehaviors, Request

# Classes:

"""

"""


class BuildRequest(Request):
    # Initialization:
    def __init__(
        self,
        AI: BotAI = None,
        ID: typing.Union[UnitTypeId, UpgradeId] = None,
        conditional: typing.Optional[typing.Callable] = None,
        target_value_or_quantity_value_behavior: typing.Union[
            RequestBehaviors.QUANTITY_BEHAVIOR, RequestBehaviors.TARGET_BEHAVIOR
        ] = RequestBehaviors.QUANTITY_BEHAVIOR,
        target_value_or_quantity_value: int = 1,
    ) -> None:
        # Initialization:
        super().__init__(
            AI=AI,
            ID=ID,
            conditional=conditional,
        )

        # Miscellaneous:
        self.target_value_or_quantity_value_behavior: typing.Union[
            RequestBehaviors.QUANTITY_BEHAVIOR, RequestBehaviors.TARGET_BEHAVIOR
        ] = target_value_or_quantity_value_behavior

        # Integers:
        self.target_value_or_quantity_value: int = target_value_or_quantity_value
        self.successions: int = 0

        # Booleans:
        self.conditional_passed_already: bool = False

    # Properties:
    @property
    def conditional_availability(self) -> bool:
        if self.conditional_passed_already:
            return True

        if self.conditional is not None:
            if not self.conditional(self.AI):
                return False

        self.conditional_passed_already = True
        return True

    @property
    def is_request_done(self) -> bool:
        match self.target_value_or_quantity_value_behavior:
            case RequestBehaviors.QUANTITY_BEHAVIOR:
                return self.successions == self.target_value_or_quantity_value
            case RequestBehaviors.TARGET_BEHAVIOR:
                return (
                    self.AI.units.of_type(self.ID).amount
                    + self.AI.already_pending(self.ID)
                    >= self.target_value_or_quantity_value
                )

    # Methods:
    async def execute(self) -> bool:
        if not self.conditional_availability:
            return False

        if self.is_request_done:
            return True

        if not self.AI.SCVManager.building_queue_empty:
            return False

        await self.AI.SCVManager.queue_building(self.ID)
        self.successions += 1

        return self.is_request_done
