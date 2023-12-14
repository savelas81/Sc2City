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


ADDON_BUILT_FROM: dict[UnitTypeId, UnitTypeId] = {
    UnitTypeId.BARRACKSREACTOR: UnitTypeId.BARRACKS,
    UnitTypeId.BARRACKSTECHLAB: UnitTypeId.BARRACKS,
    UnitTypeId.FACTORYREACTOR: UnitTypeId.FACTORY,
    UnitTypeId.FACTORYTECHLAB: UnitTypeId.FACTORY,
    UnitTypeId.STARPORTREACTOR: UnitTypeId.STARPORT,
    UnitTypeId.STARPORTTECHLAB: UnitTypeId.STARPORT,
}

NEED_TECHLAB: list[UnitTypeId] = [
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
        self.__selection_methods = {
            frozenset(UNIT_TRAINED_FROM): self.__select_to_train,
            frozenset(UPGRADE_RESEARCHED_FROM): self.__select_to_research,
            frozenset(ADDON_BUILT_FROM): self.__select_to_build,
        }

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

        if not order.id in ADDON_BUILT_FROM:
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

    # TODO: Search only through supply depots
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
        method = next(
            (
                method
                for order_set, method in self.__selection_methods.items()
                if order_id in order_set
            ),
            None,
        )
        return (
            method(order_id) if method else await self.__select_to_use_ability(order_id)
        )

    # Do we actually want random or the closest to starting position?
    def __select_to_train(self, order_id: UnitTypeId) -> Unit | None:
        structure_id = UNIT_TRAINED_FROM[order_id]
        structures = self.bot.structures(structure_id).ready
        if not structures:
            return None

        idle_structures = structures.idle
        if order_id in NEED_TECHLAB:
            return (
                idle_structures.random
                if idle_structures.filter(lambda x: x.has_techlab)
                else None
            )

        structures_with_reactors = structures.filter(
            lambda x: len(x.orders) < 2 and x.has_reactor
        )
        if structures_with_reactors:
            return structures_with_reactors.random

        return idle_structures.random if idle_structures else None

    def __select_to_research(self, order_id: UpgradeId) -> Unit | None:
        structure_id = UPGRADE_RESEARCHED_FROM[order_id]
        structures = self.bot.structures(structure_id).ready.idle
        return structures.random if structures else None

    def __select_to_build(self, order_id: UnitTypeId) -> Unit | None:
        structure_id = ADDON_BUILT_FROM[order_id]
        structures = (
            self.bot.structures(structure_id)
            .filter(lambda x: not x.has_techlab and not x.has_reactor)
            .ready.idle
        )
        return structures.random if structures else None

    async def __select_to_use_ability(self, order_id: AbilityId) -> Unit | None:
        if order_id in {
            AbilityId.CALLDOWNMULE_CALLDOWNMULE,
            AbilityId.SUPPLYDROP_SUPPLYDROP,
            AbilityId.SCANNERSWEEP_SCAN,
        }:
            return next(
                (
                    townhall
                    for townhall in self.bot.townhalls(UnitTypeId.ORBITALCOMMAND).ready
                    if townhall.energy > 50
                ),
                None,
            )

        if order_id == AbilityId.EFFECT_SALVAGE:
            return next(
                (
                    structure
                    for structure in self.bot.structures(UnitTypeId.BUNKER).ready
                    if not structure.has_cargo
                ),
                None,
            )

        return next(
            (
                structure
                for structure in self.bot.structures
                if await self.bot.can_cast(
                    structure, order_id, only_check_energy_and_cooldown=True
                )
            ),
            None,
        )

    def __select_target(self, order: Order) -> Unit | None:
        if order.id == AbilityId.CALLDOWNMULE_CALLDOWNMULE:
            # TODO prioritize mineral_field with highest content
            for townhall in self.bot.townhalls.ready:
                minerals = self.bot.mineral_field.closer_than(10, townhall.position)
                if minerals:
                    return minerals.random
        elif order.id == AbilityId.SUPPLYDROP_SUPPLYDROP:
            try:
                return self.bot.structures(
                    UnitTypeId.SUPPLYDEPOTLOWERED
                ).ready.closest_to(self.bot.start_location)
            except AssertionError:
                return self.bot.structures(UnitTypeId.SUPPLYDEPOT).ready.closest_to(
                    self.bot.start_location
                )
        return None
