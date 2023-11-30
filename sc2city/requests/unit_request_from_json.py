# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

# UnitCreationDict:
from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM

# > Units:
from sc2.units import Units

# Typing:
import typing

# Enum:
import enum

class UnitRequestFromJson:

    def __init__(self, AI: BotAI = None):
        # Miscellaneous:
        self.AI: BotAI = AI
        self.unit_to_be_trained: typing.Optional[UnitTypeId] = None
        self.amount_to_be_trained: int = 0
        self.conditional = None
        self.target_value_dict: dict = {}


    async def queue_unit(
            self,
            conditional=None,
            ID: UnitTypeId = None,
            target_value_behaviour: bool = False,
            target_value_or_quantity_value: int = 1) -> None:
        self.conditional = conditional
        self.unit_to_be_trained = ID
        if target_value_behaviour:
            if self.unit_to_be_trained not in self.target_value_dict:
                self.target_value_dict[self.unit_to_be_trained] = target_value_or_quantity_value
                print(self.target_value_dict)
        else:
            self.amount_to_be_trained = target_value_or_quantity_value

    async def unit_queue_empty(self):
        """
        checks if the unit production queue is empty.
        If queue is empty return true.
        Clears variables related to unit queue if queue is empty.
        """
        if self.amount_to_be_trained <= 0:
            self.unit_to_be_trained: typing.Optional[UnitTypeId] = None
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
            if not self.AI.can_afford(self.unit_to_be_trained):
                return
            facility_type_ids: typing.Set[UnitTypeId] = UNIT_TRAINED_FROM[self.unit_to_be_trained]
            facilities = self.AI.structures(facility_type_ids)
            if not facilities:
                return
            facilities: Units = (
                self.sort_and_filter_production_facilities(facilities=facilities)
            )
            if not facilities:
                return
            for facility in facilities:
                facility.train(self.unit_to_be_trained)
                self.amount_to_be_trained -= 1
                return

    # Methods:
    def sort_and_filter_production_facilities(
        self, facilities: Units
    ) -> typing.Optional[Units]:
        # Unit Objects:
        sorted_and_filtered_facilities: Units = Units([], self.AI)
        facilities_without_add_on: Units = Units([], self.AI)
        facilities_with_reactor: Units = Units([], self.AI)
        facilities_with_techlab: Units = Units([], self.AI)

        # Constants:
        townhall_types: typing.Set[UnitTypeId] = {
            UnitTypeId.COMMANDCENTER,
            UnitTypeId.PLANETARYFORTRESS,
            UnitTypeId.ORBITALCOMMAND,
        }

        need_techlab: typing.Set[UnitTypeId] = {
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
                and self.ID not in need_techlab
            ):
                facilities_with_reactor.append(facility)
            elif facility.has_techlab and facility.is_idle:
                facilities_with_techlab.append(facility)
            elif facility.is_idle and self.ID not in need_techlab:
                facilities_without_add_on.append(facility)

        sorted_and_filtered_facilities.append(facilities_with_reactor)
        sorted_and_filtered_facilities.append(facilities_with_techlab)
        sorted_and_filtered_facilities.append(facilities_without_add_on)
        return sorted_and_filtered_facilities
