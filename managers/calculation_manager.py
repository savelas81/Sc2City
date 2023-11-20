# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > Cost:
from sc2.game_data import Cost

# Typing:
import typing


# Classes:

"""
* A manager used to calculate resources lost from units
*
* @param AI --> The SC2City AI object.
*
"""


class CalculationManager:
    # Initialization:
    def __init__(self, AI: BotAI = None) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

    # Methods:
    """
    * A property returning a dictionary containing the amount of minerals and vespene the enemy lost.
    *
    * @returns A dictionary containing the amount of minerals and vespene the enemy lost.
    """

    @property
    def enemy_lost_resources(self) -> typing.Dict[str, int]:
        resources: typing.Dict[str, int] = {
            "minerals": 0,
            "vespene": 0,
        }

        for enemy_unit in self.AI.MemoryManager.dead_enemy_units:
            value: Cost = self.AI.calculate_unit_value(enemy_unit.type_id)

            resources["minerals"] += value.minerals
            resources["vespene"] += value.vespene

        return resources

    """
    * A property returning a dictionary containing the amount of minerals and vespene we lost.
    *
    * @returns A dictionary containing the amount of minerals and vespene the we lost.
    """

    @property
    def friendly_lost_resources(self) -> typing.Dict[str, int]:
        resources: typing.Dict[str, int] = {
            "minerals": 0,
            "vespene": 0,
        }

        for friendly_unit in self.AI.MemoryManager.dead_friendly_units:
            value: Cost = self.AI.calculate_unit_value(friendly_unit.type_id)

            resources["minerals"] += value.minerals
            resources["vespene"] += value.vespene

        return resources
