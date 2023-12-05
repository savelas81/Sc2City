# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId

# Typing:
import typing

# Loguru:
import loguru

# Requests:
from sc2city.requests import UnitRequest


# Classes:

"""
* A manager that executes unit requests.
*
* @param AI --> The SC2City AI object.
*
* @param debug --> A setting to enable debugging features for functions.
*
* NOTE: The executor's sole purpose is to execute the request and put the unit into production..
    * It does not verify that the request's unit's training is fully completed.
"""


class UnitRequestExecutor:
    # Initialization:
    def __init__(self, AI: BotAI = None, debug: bool = False) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

        # Booleans:
        self.debug: bool = debug

        # Lists:
        self.unit_requests: typing.List[UnitRequest] = []
        self.verifying: typing.List[UnitRequest] = []

    # Methods:
    def _is_there_existing_unit_request(self, ID: UnitTypeId) -> bool:
        for unit_request in self.verifying:
            if unit_request.ID == ID:
                return True

        return False

    def queue_request(self, request) -> None:
        self.unit_requests.append(request)

    def on_step(self) -> None:
        completed: typing.Set[UnitRequest] = set()

        for unit_request in self.unit_requests:
            if self._is_there_existing_unit_request(unit_request.ID):
                continue

            if unit_request.conditional_availability:
                self.verifying.append(unit_request)

                if self.debug:
                    loguru.logger.info(
                        f"Appending unit request with ID {unit_request.ID} to queue."
                    )
                    loguru.logger.info("-" * 30)

        for unit_request in self.verifying:
            if unit_request in self.unit_requests:
                self.unit_requests.remove(unit_request)

            result: bool = unit_request.execute()
            if result:
                completed.add(unit_request)

                if self.debug:
                    loguru.logger.info(
                        f"Unit request with ID {unit_request.ID} has completed successfully.. removing."
                    )

        for unit_request in completed:
            if unit_request in self.verifying:
                self.verifying.remove(unit_request)
