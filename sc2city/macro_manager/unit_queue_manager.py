from typing import TYPE_CHECKING, Optional

from sc2.ids.unit_typeid import UnitTypeId
from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM
from sc2.units import Units

if TYPE_CHECKING:
    from Sc2City import Sc2City


class UnitQueueManager:
    def __init__(self, bot: "Sc2City"):
        # Miscellaneous:
        self.bot = bot
        self.unit_to_be_trained: Optional[UnitTypeId] = None
        self.amount_to_be_trained: int = 0
        self.conditional = None
        self.target_value_dict: dict = {}

    async def queue_unit(
        self,
        conditional=None,
        ID: UnitTypeId = None,
        target_value_behaviour: bool = False,
        target_value_or_quantity_value: int = 1,
    ) -> None:
        self.conditional = conditional
        self.unit_to_be_trained = ID
        if target_value_behaviour:
            if self.unit_to_be_trained not in self.target_value_dict:
                self.target_value_dict[
                    self.unit_to_be_trained
                ] = target_value_or_quantity_value
                print(self.target_value_dict)
                self.unit_to_be_trained = None
        else:
            self.amount_to_be_trained = target_value_or_quantity_value

    async def unit_queue_empty(self):
        """
        checks if the unit production queue is empty.
        If queue is empty return true.
        Clears variables related to unit queue if queue is empty.
        """
        if self.amount_to_be_trained <= 0 or self.unit_to_be_trained is None:
            self.unit_to_be_trained: Optional[UnitTypeId] = None
            self.amount_to_be_trained: int = 0
            self.conditional = None
            return True
        else:
            return False

    async def execute_build_units(self):
        """
        Build units that are in self.unit_to_be_trained or if that is empty then we train unit
        from self.target_value_dict = {UnitTypeId : target_amount}
        """
        if self.unit_to_be_trained:
            if not self.bot.can_afford(self.unit_to_be_trained):
                return
            facility_type_ids: set[UnitTypeId] = UNIT_TRAINED_FROM[
                self.unit_to_be_trained
            ]
            facilities = self.bot.structures(facility_type_ids)
            if not facilities:
                return
            facilities: Units = self.sort_and_filter_production_facilities(
                facilities=facilities, unit_type_id=self.unit_to_be_trained
            )
            if not facilities:
                return
            for facility in facilities:
                print(facility)
                facility.train(self.unit_to_be_trained)
                self.amount_to_be_trained -= 1
                return
        else:
            await self.execute_target_value_dict()
            return

    async def execute_target_value_dict(self):
        for unit_id in self.target_value_dict:
            target_amount = self.target_value_dict[unit_id]
            if self.bot.units(unit_id).amount + self.bot.already_pending(
                unit_id
            ) < target_amount and self.bot.can_afford(unit_id):
                facility_type_ids: set[UnitTypeId] = UNIT_TRAINED_FROM[unit_id]
                facilities = self.bot.structures(facility_type_ids)
                if not facilities:
                    return
                facilities: Units = self.sort_and_filter_production_facilities(
                    facilities=facilities, unit_type_id=unit_id
                )
                if not facilities:
                    return
                for facility in facilities:
                    facility.train(unit_id)
                    return

    # Methods:
    def sort_and_filter_production_facilities(
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
