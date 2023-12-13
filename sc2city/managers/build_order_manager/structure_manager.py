from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM
from sc2.dicts.upgrade_researched_from import UPGRADE_RESEARCHED_FROM
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.units import Units

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

NEED_TECHLAB = [
    UnitTypeId.MARAUDER,
    UnitTypeId.GHOST,
    UnitTypeId.SIEGETANK,
    UnitTypeId.CYCLONE,
    UnitTypeId.THOR,
    UnitTypeId.MARAUDER,
    UnitTypeId.RAVEN,
    UnitTypeId.BANSHEE,
    UnitTypeId.BATTLECRUISER,
]


class StructureManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    async def produce(self, order: Order) -> bool:
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
            structure = await self.__select_structure(order.id)
            if not structure:
                return order.can_skip
            order.tag = structure.tag
        else:
            structure = self.bot.structures.find_by_tag(order.tag)

        if order.id in UPGRADE_RESEARCHED_FROM:
            structure.research(order.id)
        else:
            structure.train(order.id)
        # TODO: Fix bugs with the starting queue
        order.update_status(Status.STARTED)
        return False

    async def execute_action(self, order: Order) -> bool:
        """
        Returns False when executing orders to avoid double commands.
        """
        if not order.tag:
            structure = await self.__select_structure(order.id)
            if not structure:
                return order.can_skip
            order.tag = structure.tag
        else:
            structure = self.bot.structures.find_by_tag(order.tag)

        if not order.target:
            order.target = self.__select_target(order)

        if not await self.bot.can_cast(structure, order.id, order.target):
            return order.can_skip

        structure(order.id, order.target)
        order.update_status(Status.STARTED)  # TODO: Move this to build order manager

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

    async def __select_structure(
        self, order_id: UnitTypeId | UpgradeId | AbilityId
    ) -> Unit | None:
        structure_id = None
        if order_id in UNIT_TRAINED_FROM:
            structure_id = UNIT_TRAINED_FROM[order_id]
        elif order_id in UPGRADE_RESEARCHED_FROM:
            structure_id = UPGRADE_RESEARCHED_FROM[order_id]
        elif order_id in ADDON_BUILT_FROM:
            structure_id = ADDON_BUILT_FROM[order_id]
        else:
            # TODO: Optimize searches by structure type
            for structure in self.bot.structures:
                if await self.bot.can_cast(
                    structure, order_id, only_check_energy_and_cooldown=True
                ):
                    return structure
        if not structure_id:
            return None

        structures = self.bot.structures(structure_id).ready  # we can use only ready structures
        if not structures:
            return None
        if order_id in UNIT_TRAINED_FROM:
            return self.__select_best_structure_to_train_unit(structures=structures, order_id=order_id)
        elif order_id in UPGRADE_RESEARCHED_FROM:
            if structures.idle:
                return structures.idle.random
        elif order_id in ADDON_BUILT_FROM:
            structures_without_addon = structures.filter(lambda x: not x.has_techlab and not x.has_reactor).idle
            if structures_without_addon:
                return structures_without_addon.random
        return None

    def __select_best_structure_to_train_unit(self, structures: Units, order_id: UnitTypeId) -> Unit | None:
        if structures.first in self.bot.townhalls:
            townhalls = structures.idle
            if townhalls:
                return townhalls.random
            else:
                return None
        if order_id not in NEED_TECHLAB:  # when training marines etc. we want to prioritise reactors
            structures_with_reactors = structures.filter(lambda x: len(x.orders) < 2 and x.has_reactor)
            if structures_with_reactors:
                return structures_with_reactors.random
        structures_with_techlabs = structures.idle.filter(lambda x: x.has_techlab)
        if structures_with_techlabs:  # prioritise structures with techlabs over structures without addon
            return structures.random
        if structures.idle:  # if we have any idle structures one of them is used
            return structures.idle.random
        return None

    def __select_target(self, order: Order) -> Unit | None:
        if order.id == AbilityId.CALLDOWNMULE_CALLDOWNMULE:
            # TODO prioritise mineral_field with highest content
            for townhall in self.bot.townhalls.ready:
                minerals = self.bot.mineral_field.closer_than(10, townhall.position)
                if minerals:
                    return minerals.random
        elif order.id == AbilityId.SUPPLYDROP_SUPPLYDROP:
            self.bot.structures(UnitTypeId.SUPPLYDEPOT).closest_to(
                self.bot.start_location
            )
        return None
