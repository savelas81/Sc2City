# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

# Typing:
import typing

# Enum:
import enum

# Classes:

"""
* Enumerations for request subclasses indicating the behavior of the specified variable.
*
"""


class RequestBehaviors(enum.Enum):
    QUANTITY_BEHAVIOR = enum.auto()
    TARGET_BEHAVIOR = enum.auto()


"""
* Request class that contains methods to be overridden.
*
* @param AI --> The SC2City AI object.
*
* @param ID --> The ID of the wanted unit, structure, or upgrade.
*
* @param callable --> A function or lambda that will be called with the AI parameter.
    * example usage: lambda AI: AI.minerals >= 500
    * example usage: def foo(AI):
                        return True
    *
*
* More parameters can be added in the subclass implementations.
*
"""


class Request:
    # Initialization:
    def __init__(
        self,
        AI: BotAI = None,
        ID: typing.Union[UnitTypeId, UpgradeId] = None,
        conditional: typing.Optional[typing.Callable] = None,
        *args,
        **kwargs
    ) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI
        self.ID: typing.Union[UnitTypeId, UpgradeId] = ID
        self.conditional: typing.Optional[typing.Callable] = conditional

    # Methods:

    """
    * Method to execute the request. Should be overriden.
    *
    * @returns A boolean indicating whether the request is done.
    """

    async def execute(self) -> bool:
        pass
