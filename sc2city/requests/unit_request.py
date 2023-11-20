# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > Units:
from sc2.units import Units

# > Units:
from sc2.unit import Unit

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId

# Typing:
import typing

# Loguru:
import loguru

# Request:
from .request import RequestBehaviors, Request

# Dictionaries:

UNIT_TYPE_ID_TO_PRODUCTION_FACILITY: typing.Dict[UnitTypeId, typing.Set[UnitTypeId]] = {
    UnitTypeId.SCV: {
        UnitTypeId.COMMANDCENTER,
        UnitTypeId.PLANETARYFORTRESS,
        UnitTypeId.ORBITALCOMMAND,
    },
    UnitTypeId.MARINE: {UnitTypeId.BARRACKS},
    UnitTypeId.MARAUDER: {UnitTypeId.BARRACKS},
}

# Classes:

"""
* Unit request class that is used to produce a unit.
*
* @param AI --> The SC2City AI object.
*
* @param ID --> The ID of the wanted unit or structure.
*
"""


# TODO: Make priorities for units.. e.g marines go to reactors Check: def sort_and_filter_production_facilitie
# TODO: Possibly a queue manager
class UnitRequest(Request):
    # Initialization:
    def __init__(
        self,
        AI: BotAI = None,
        ID: UnitTypeId = UnitTypeId.SCV,
        conditional: typing.Optional[typing.Callable] = None,
        target_value_or_quantity_value_behavior: typing.Union[
            RequestBehaviors.QUANTITY_BEHAVIOR, RequestBehaviors.TARGET_BEHAVIOR
        ] = RequestBehaviors.QUANTITY_BEHAVIOR,
        target_value_or_quantity_value: int = 1,
    ) -> None:
        # Initialization:
        super().__init__(AI=AI, ID=ID, conditional=conditional)

        # Miscellaneous:
        self.target_value_or_quantity_value_behavior = (
            target_value_or_quantity_value_behavior
        )
        self.target_value_or_quantity_value = target_value_or_quantity_value

        # Booleans:
        self.conditional_passed_already: bool = False

        # Integers:
        self.successions: int = 0

    # Properties:
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

    @property
    def conditional_availability(self) -> bool:
        if self.conditional_passed_already:
            return True

        if self.conditional is not None:
            if not self.conditional(self.AI):
                return False

        self.conditional_passed_already = True
        return True

    # Methods:
    def execute(self) -> bool:
        if self.is_request_done:
            return True

        if not self.conditional_availability:
            return False

        if self.AI.supply_left < self.AI.calculate_supply_cost(self.ID):
            return False

        production_facilities: typing.Optional[
            typing.Dict[UnitTypeId, typing.Set[UnitTypeId]]
        ] = UNIT_TYPE_ID_TO_PRODUCTION_FACILITY.get(self.ID, None)

        if production_facilities is None:
            loguru.logger.error(f"There is no production facility for ID {self.ID}")

            return False

        available_production_facilities: Units = self.AI.structures.of_type(
            production_facilities
        ).ready.idle
        if not any(available_production_facilities):
            return False

        for available_production_facility in available_production_facilities:
            if self.is_request_done:
                return True

            if self.AI.can_afford(self.ID):
                available_production_facility.train(self.ID)

                if (
                    self.target_value_or_quantity_value_behavior
                    == RequestBehaviors.QUANTITY_BEHAVIOR
                ):
                    self.successions += 1
            else:
                return False


    def sort_and_filter_production_facilitie(self, faclilities: Units) -> Optional[Units]:
        facilities_without_add_on = sc2.units.Units([], self.AI) # empty units object
        facilities_with_reactor = sc2.units.Units([], self.AI)
        facilities_with_techlab = sc2.units.Units([], self.AI)
        townhall_types = [UnitTypeId.COMMANDCENTER, UnitTypeId.PLANETARYFORTRESS, UnitTypeId.ORBITALCOMMAND]
        sorted_and_filtered_facilities = sc2.units.Units([], self.AI)
        need_techlab = [
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

        for facility in faclilities.ready.idle:
            if facility.type_id in townhall_types:
                sorted_and_filtered_facilities.append(facility)
        if sorted_and_filtered_facilities:
            return sorted_and_filtered_facilities

        for facility in faclilities.ready:
            if facility.has_ractor and len(facility.orders) < 2 and self.ID not in need_techlab:
                facilities_with_reactor.apped(facility)
            elif facility.has_techlab and facility.is_idle:
                facilities_with_reactor.apped(facility)
            elif facility.is_idle and self.ID not in need_techlab:
                facilities_without_add_on.append(facility)
        sorted_and_filtered_facilities.append(facilities_with_reactor)
        sorted_and_filtered_facilities.append(facilities_with_techlab)
        sorted_and_filtered_facilities.append(facilities_without_add_on)
        return sorted_and_filtered_facilities
