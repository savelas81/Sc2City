# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# Typing:
import typing

# Loguru:
import loguru

# Requests:
from sc2city.requests import BuildRequest


# Classes:

"""
* A manager that executes build requests.
*
* @param AI --> The SC2City AI object.
*
* @param debug --> A setting to enable debugging features for functions.
*
"""

class BuildRequestExecutor:
    # Initialization:
    def __init__(self, AI: BotAI, debug: bool = False) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

        # Booleans:
        self.debug: bool = debug

        # Lists:
        self.build_requests: typing.List[BuildRequest] = []
        self.verifying: typing.List[BuildRequest] = []

    # Methods:
    def on_step(self) -> None:
        pass
