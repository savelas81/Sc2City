from typing import TYPE_CHECKING, Optional

from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM
from sc2.ids.unit_typeid import UnitTypeId
from sc2.units import Units

from utils import Status, OrderType

if TYPE_CHECKING:
    from Sc2City import Sc2City


# TODO: Add logic for controlling movable structures
class StructureManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    # TODO: Add logic for add-ons, researches and building upgrades (e.g. planetary fortress)
    def execute_builds(self) -> None:
        self.__train_units()

    # TODO: Improve logic and refactor
    # TODO: Implement logic for conditional orders
    # TODO: Improve logic for handling multiple orders
    # TODO: Add logic to handle for interruptions
    def __train_units(self) -> None:
        for order in self.bot.queues[OrderType.UNIT]:
            if order.status != Status.PENDING:
                continue
            if not self.bot.can_afford(order.id):
                return
            facility = UNIT_TRAINED_FROM[order.id]
            facilities = self.bot.structures(facility)
            if facilities:
                facilities = self.__sort_and_filter_production_facilities(
                    facilities, order.id
                )
            if not facilities:
                continue
            for facility in facilities:
                facility.train(order.id)
                order.status = Status.STARTED

    #  TODO: Improve this logic and the parameters used
    def __sort_and_filter_production_facilities(
        self, facilities: Units, unit_type_id: UnitTypeId = None
    ) -> Optional[Units]:
        # Unit Objects:
        sorted_and_filtered_facilities: Units = Units([], self.bot)
        facilities_without_add_on: Units = Units([], self.bot)
        facilities_with_reactor: Units = Units([], self.bot)
        facilities_with_techlab: Units = Units([], self.bot)

        # Constants:
        townhall_types: set[UnitTypeId] = {
            UnitTypeId.COMMANDCENTER,
            UnitTypeId.PLANETARYFORTRESS,
            UnitTypeId.ORBITALCOMMAND,
        }

        need_techlab: set[UnitTypeId] = {
            UnitTypeId.MARAUDER,
            UnitTypeId.GHOST,
            UnitTypeId.SIEGETANK,
            UnitTypeId.CYCLONE,
            UnitTypeId.THOR,
            UnitTypeId.MARAUDER,
            UnitTypeId.RAVEN,
            UnitTypeId.BANSHEE,
            UnitTypeId.BATTLECRUISER,
        }

        # Main:
        facility_is_cc = False
        for facility in facilities:
            if facility.type_id in townhall_types:
                facility_is_cc = True
                if not facility.is_ready:
                    continue
                # TODO do we have to check if the structure is idle.
                # TODO or do we sort building somehow. Needs testing
                if not facility.is_idle:
                    continue
                sorted_and_filtered_facilities.append(facility)
        if facility_is_cc:
            return sorted_and_filtered_facilities

        for facility in facilities.ready:
            if (
                facility.has_reactor
                and len(facility.orders) < 2
                and unit_type_id not in need_techlab
            ):
                facilities_with_reactor.append(facility)
            elif facility.has_techlab and facility.is_idle:
                facilities_with_techlab.append(facility)
            elif facility.is_idle and unit_type_id not in need_techlab:
                facilities_without_add_on.append(facility)

        sorted_and_filtered_facilities = (
            facilities_with_reactor
            | facilities_with_techlab
            | facilities_without_add_on
        )
        return sorted_and_filtered_facilities
