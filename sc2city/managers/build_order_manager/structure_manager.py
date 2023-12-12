from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM
from sc2.dicts.upgrade_researched_from import UPGRADE_RESEARCHED_FROM
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId

from utils import Status
from game_objects import Order

if TYPE_CHECKING:
    from Sc2City import Sc2City


ADDON_BUILT_FROM = {
    UnitTypeId.BARRACKSREACTOR: UnitTypeId.BARRACKS,
    UnitTypeId.BARRACKSTECHLAB: UnitTypeId.BARRACKS,
    UnitTypeId.FACTORYREACTOR: UnitTypeId.FACTORY,
    UnitTypeId.FACTORYTECHLAB: UnitTypeId.FACTORY,
    UnitTypeId.STARPORTREACTOR: UnitTypeId.STARPORT,
    UnitTypeId.STARPORTTECHLAB: UnitTypeId.STARPORT,
}


class StructureManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def produce(self, order: Order) -> bool:
        """
        Executes the given order by producing the specified unit or upgrading/researching
        the specified technology.

        Args:
            order (Order): The order to be executed.

        Returns:
            bool: False if the order is being executed to avoid double commands.

        """
        if self.bot.tech_requirement_progress(order.id) != 1 or not self.bot.can_afford(
            order.id
        ):
            return order.can_skip

        if not order.tag:
            structure = self.__select_structure(order.id)
            if not structure:
                return order.can_skip
            order.tag = structure.tag
        else:
            structure = self.bot.structures.find_by_tag(order.tag)

        if order.id in UPGRADE_RESEARCHED_FROM:
            structure.research(order.id)
        else:
            structure.train(order.id)
        order.update_status(Status.STARTED)  # TODO: Move this to build order manager
        return False

    async def execute_action(self, order: Order) -> bool:
        """
        Returns False when executing orders to avoid double commands.
        """
        if not order.tag:
            structure = self.__select_structure()
            order.tag = structure.tag
        else:
            structure = self.bot.structures.find_by_tag(order.tag)

        if not order.target:
            order.target = self.__select_target()

        await self.bot.can_cast(structure, order.id, order.target)

        # Test if abilities without a target break when sending with None
        structure(order.id, order.target)

    # TODO: Create specific sets for each type of structure
    # TODO: Improve this logic and refactor (Try to not go through all enemies every step)
    def handle_supply_depots(self) -> None:
        for structure in self.bot.structures:
            if structure.type_id not in {
                UnitTypeId.SUPPLYDEPOT,
                UnitTypeId.SUPPLYDEPOTLOWERED,
            }:
                continue
            enemies = self.bot.enemy_units.closer_than(
                structure.sight_range, structure
            ).not_flying
            if structure.type_id == UnitTypeId.SUPPLYDEPOT and not enemies:
                structure(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
            elif structure.type_id == UnitTypeId.SUPPLYDEPOTLOWERED and enemies:
                structure(AbilityId.MORPH_SUPPLYDEPOT_RAISE)

    def __select_structure(self, order_id: UnitTypeId | UpgradeId) -> Unit | None:
        if order_id in UNIT_TRAINED_FROM:
            structure_id = UNIT_TRAINED_FROM[order_id]
        elif order_id in UPGRADE_RESEARCHED_FROM:
            structure_id = UPGRADE_RESEARCHED_FROM[order_id]
        elif order_id in ADDON_BUILT_FROM:
            structure_id = ADDON_BUILT_FROM[order_id]
        else:
            return None

        # This might be a problem for buildings that can train multiple units at the same time
        # TODO: Add better logic for choosing structure
        structures = self.bot.structures(structure_id).idle.ready
        if not structures:
            return None
        structure = structures.random
        return structure
