# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > Units:
from sc2.units import Units

# > Unit:
from sc2.unit import Unit

# Typing:
import typing

# Loguru:
import loguru

# Classes:

"""
* Manager that is in charge of keeping track of unit objects.
*
* @param AI --> The SC2City AI object.
*
* @param debug --> A setting to enable debugging features for functions.
*
"""


class MemoryManager:
    # Initialization:
    def __init__(self, AI: BotAI = None, debug: bool = False) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

        # Dictionaries:
        self.friendly_unit_tag_to_unit_object: typing.Dict[int, Unit] = dict()
        self.enemy_unit_tag_to_unit_object: typing.Dict[int, Unit] = dict()

        # Booleans:
        self.debug: bool = debug

        # Sets:
        self.dead_friendly_units: Units = Units([], AI)
        self.dead_enemy_units: Units = Units([], AI)

    # Methods:
    """
    * Method to remember units.
    *   Should be called every frame OR on any function related to vision changes..
    *
    """

    def remember_units(self) -> None:
        # NOTE: Savelas were you high when you wrote this if-statement? ~ Christopher
        #       * Not sure if it is necessary...

        # Enemy Units:
        for enemy_unit in self.AI.all_enemy_units:
            if self.enemy_unit_tag_to_unit_object.get(enemy_unit.tag) is None:
                self.enemy_unit_tag_to_unit_object[enemy_unit.tag] = enemy_unit

                # Debugging:
                if self.debug is True:
                    loguru.logger.info(
                        f"Unit with tag {enemy_unit.tag} and type {enemy_unit.type_id} was added into enemy unit memory.",
                    )

                    loguru.logger.info("-" * 30)
            else:
                self.enemy_unit_tag_to_unit_object.update({enemy_unit.tag: enemy_unit})

        # Friendly Units:
        for friendly_unit in self.AI.units | self.AI.structures:
            if self.friendly_unit_tag_to_unit_object.get(friendly_unit.tag) is None:
                self.friendly_unit_tag_to_unit_object[friendly_unit.tag] = friendly_unit

                # Debugging:
                if self.debug is True:
                    loguru.logger.info(
                        f"Unit with tag {friendly_unit.tag} and type {friendly_unit.type_id} was added into friendly unit memory.",
                    )

                    loguru.logger.info("-" * 30)
            else:
                self.friendly_unit_tag_to_unit_object.update(
                    {friendly_unit.tag: friendly_unit}
                )

    """
    * Method to keep track of dead units.
    *   Should be called in functions relating to death of friendly or enemy units.
    *
    """

    def forget_unit(self, unit_tag: int) -> None:
        # Enemy Units:
        if self.enemy_unit_tag_to_unit_object.get(unit_tag) is not None:
            self.dead_enemy_units.append(
                self.enemy_unit_tag_to_unit_object.pop(unit_tag)
            )

            # Debugging:
            if self.debug is True:
                loguru.logger.info(
                    f"Unit with tag {unit_tag} was added into dead enemy unit memory.",
                )

                loguru.logger.info("-" * 30)

            return None

        # Friendly Units:
        if self.friendly_unit_tag_to_unit_object.get(unit_tag) is not None:
            self.dead_friendly_units.append(
                self.friendly_unit_tag_to_unit_object.pop(unit_tag)
            )

            # Debugging:
            if self.debug is True:
                loguru.logger.info(
                    f"Unit with tag {unit_tag} was added into friendly enemy unit memory.",
                )

                loguru.logger.info("-" * 30)

            return None

        loguru.logger.error(
            f"Unit of {unit_tag} not in friendly unit memory or enemy unit memory.."
        )
