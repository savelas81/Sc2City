# Imports:

# StarCraft II:
# > Position:
from sc2.position import Point2

# > Bot AI:
from sc2.bot_ai import BotAI

# > Units:
from sc2.units import Units

# > Unit:
from sc2.unit import Unit

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId

# Typing:
import typing

# Loguru:
import loguru

# Math:
import math

# Utils:
from sc2city.util import SCVManagerUtil

# Constants:

SCV_RADIUS: float = 0.375

# Classes:

"""
DOCUMENTATION HERE SAVELAS OR MARLON!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""


class SCVManager:
    # Constants:
    SCVs_PER_REFINERY: int = 3
    GAS_MINERS_TOTAL: int = 50

    # Initialization:
    def __init__(self, AI: BotAI = None, debug: bool = False):
        # Miscellaneous:
        self.AI: BotAI = AI

        self.SCVManagerUtil: SCVManagerUtil = SCVManagerUtil(AI=AI)

        self.next_building_position = Point2((0, 0))
        self.next_building_type = None

        # Dictionaries:
        self.mineral_collector_dict: typing.Dict[int, int] = {}
        self.vespene_collector_dict: typing.Dict[int, int] = {}

        # Integers:
        self.first_builder_tag: int = 0
        self.builder_tag: int = 0

        self.queue_delay: int = 3

        # Booleans:
        self.remember_first_builder = True
        self.expand_to_natural: typing.Union[Point2, bool] = True

        self.debug: bool = debug

        # Lists:
        self.interrupted_building_types: typing.List = []

        self.repairer_tag_list: typing.List[int] = []
        self.boys_tag_list: typing.List[int] = []

        self.active_builders_tag_list = []
        self.scout_tag_list = []

        self.placeholders = []

    # Properties:
    """
    implementation is kind of obvious but still MARLONNNNN SAVELASS ADD DOC HERE!!!! u fucking monsters
    """

    @property
    def building_queue_empty(self) -> bool:
        if (
            self.next_building_type is None
            and self.queue_delay <= 0
            and not self.AI.placeholders
            and len(self.placeholders) == 0
            and len(self.interrupted_building_types) == 0
        ):
            return True
        else:
            return False

    # Methods:

    """
    MARLON! SAVELAS! U know what to do here.........
    """

    # TODO: Have chronicles fix this function and make it better...

    async def worker_split_frame_zero(self) -> None:
        # Miscellaneous:
        self.expand_to_natural: typing.Optional[
            Point2
        ] = await self.AI.get_next_expansion()

        # Variables:
        mineral_fields: Units = self.AI.mineral_field.closer_than(
            distance=10, position=self.AI.townhalls.first.position
        )
        workers: Units = self.AI.units.of_type(UnitTypeId.SCV)

        if not any(workers):
            loguru.logger.info("SAVELASSSSSSSSS MARLONNNNNNNNNNNNNNNN")

        # Main:
        for mineral_field in mineral_fields:
            worker: Unit = workers.closest_to(mineral_field)
            worker.gather(mineral_field)

            self.mineral_collector_dict[worker.tag] = mineral_field.tag
            workers.remove(worker)

        for worker in workers:
            mineral_field: Unit = mineral_fields.closest_to(worker)
            worker.gather(mineral_field)

            self.mineral_collector_dict[worker.tag] = mineral_field.tag

    """
    Doc here...
    
    TODO: Please shorten this code... maybe add some stuff to other methods to condense it and make it cleaner
    """

    async def queue_building(
        self, structure_type_id: UnitTypeId = UnitTypeId.BARRACKS
    ) -> None:
        # Debugging:
        if self.debug:
            loguru.logger.info(
                "SCVManager: Queuing building: {}".format(str(structure_type_id))
            )

        # Refinery Handling...
        if structure_type_id == UnitTypeId.REFINERY:
            self.next_building_type = structure_type_id

            return None

        # Main:
        position: typing.Optional[
            Point2
        ] = await self.AI.BuildingPlacementSolver.get_placement_for(
            structure_type_id=structure_type_id
        )

        if position is None:
            loguru.logger.info(
                f"Position is None for some reason..... Structure Type ID: {str(structure_type_id)}"
            )
            return None
        else:
            if self.expand_to_natural and structure_type_id == UnitTypeId.COMMANDCENTER:
                position: typing.Union[Point2, bool] = self.expand_to_natural
                if isinstance(position, bool):
                    loguru.logger.info(
                        "Position is a boolean but we wanted a Point2..."
                    )

                    return None

                self.expand_to_natural: typing.Union[Point2, bool] = False

            if self.first_builder_tag != 0:
                contractor = self.first_builder_tag

                self.first_builder_tag = 0
            else:
                contractor = await self.select_contractor(position=position)

            if self.remember_first_builder:
                self.first_builder_tag: int = contractor
                self.remember_first_builder: bool = False

            if not contractor:
                loguru.logger.info("No contractor was selected!")
                return None

            await self.remove_unit_tag_from_lists(contractor.tag)
            self.builder_tag = contractor.tag
            self.next_building_type = structure_type_id
            self.next_building_position = Point2(position)
            contractor.move(self.next_building_position)

    async def select_contractor(self, position: Point2) -> typing.Optional[Unit]:
        if not position:
            print("scv_manager: No position for building!")
            return None
        scvs = self.AI.units(UnitTypeId.SCV)
        for scv in scvs.sorted(lambda x: x.distance_to(position)):
            # TODO select closest by pathing. Now by distance.
            if scv.tag not in self.mineral_collector_dict:
                continue
            if scv.is_carrying_resource:
                continue
            return scv
        print("scv_manager: No valid scv for builder!")
        return None

    async def move_scvs(self):
        self.queue_delay -= 1
        await self.placeholder_tracker()
        await self.distribute_workers()
        await self.build_queued_building()

    async def placeholder_tracker(self):
        for holder in self.AI.placeholders:
            self.queue_delay: int = 3
            if holder in self.placeholders:
                continue
            else:
                self.placeholders.append(holder)

        holder_to_be_deleted = None
        for holder_in_memory in self.placeholders:
            if self.AI.structures.closer_than(1, holder_in_memory.position):
                structure = self.AI.structures.closest_to(holder_in_memory.position)
                if structure.type_id == holder_in_memory.type_id:
                    print("Building started successfully.")
                    holder_to_be_deleted = holder_in_memory
                    break
            elif self.queue_delay <= 0 and not self.AI.placeholders.closer_than(
                1, holder_in_memory
            ):
                loguru.logger.info(
                    f"Was not able to start building Type ID: {str(holder_in_memory.type_id)}"
                )
                await self.queue_building(holder_in_memory.type_id)
                holder_to_be_deleted = holder_in_memory
        if holder_to_be_deleted:
            self.placeholders.remove(holder_to_be_deleted)

    async def add_unit_tag_scout_list(self, unit_tag: int):
        await self.remove_unit_tag_from_lists(unit_tag=unit_tag)
        self.scout_tag_list.append(unit_tag)

    async def build_queued_building(self):
        if self.building_queue_empty or self.next_building_type is None:
            return

        if self.next_building_type == UnitTypeId.REFINERY:
            if self.AI.can_afford(self.next_building_type):
                for cc in self.AI.townhalls.sorted(
                    lambda unit: unit.is_ready, reverse=True
                ):
                    geysers = self.AI.vespene_geyser.closer_than(10.0, cc)
                    for geyser in geysers:
                        point = geyser.position.towards(self.AI.game_info.map_center, 2)
                        if not self.AI.gas_buildings.closer_than(
                            1.0, geyser
                        ) and not self.AI.placeholders.closer_than(1.0, geyser):
                            contractor = await self.select_contractor(position=point)
                            if contractor is None:
                                return
                            contractor.build(UnitTypeId.REFINERY, geyser)
                            self.queue_delay = 3
                            print(
                                "Scv building "
                                + str(self.next_building_type)
                                + " at time "
                                + str(self.AI.time_formatted)
                                + " minerals "
                                + str(self.AI.minerals)
                                + " vespene "
                                + str(self.AI.vespene)
                            )
                            if contractor.tag in self.mineral_collector_dict:
                                self.mineral_collector_dict.pop(contractor.tag)
                            if contractor.tag not in self.active_builders_tag_list:
                                self.active_builders_tag_list.append(contractor.tag)
                            self.next_building_type = None
                            return
        else:
            if self.AI.can_afford(self.next_building_type):
                for scv in self.AI.units(UnitTypeId.SCV):
                    if scv.tag == self.builder_tag:
                        scv.build(self.next_building_type, self.next_building_position)
                        self.queue_delay = 3
                        print(
                            "Scv building "
                            + str(self.next_building_type)
                            + " at time "
                            + str(self.AI.time_formatted)
                            + " minerals "
                            + str(self.AI.minerals)
                            + " vespene "
                            + str(self.AI.vespene)
                        )
                        if self.builder_tag not in self.active_builders_tag_list:
                            self.active_builders_tag_list.append(self.builder_tag)
                        self.builder_tag: int = 0
                        self.next_building_type = None
                        self.next_building_position = Point2((0, 0))
                        return
                print("scv_manager: No scv tags match self.builder_tag")
                return

    async def distribute_workers(self):
        # TODO distribute scvs mineral miners between bases
        """Calculate custom_assigned_harvesters for CC, REFINERY and MINERALFIELD"""
        for structure in (
            self.AI.gas_buildings | self.AI.townhalls | self.AI.mineral_field
        ):
            structure.custom_assigned_harvesters = 0
            structure.custom_surplus_harvesters = 0
        for target_refinery_tag in self.vespene_collector_dict.values():
            refinery = self.AI.gas_buildings.ready.find_by_tag(target_refinery_tag)
            if refinery:
                refinery.custom_assigned_harvesters += 1
                continue
        for scv in self.AI.units(UnitTypeId.SCV):
            if scv.tag in self.mineral_collector_dict:
                target_mf_tag = self.mineral_collector_dict[scv.tag]
                mf = self.AI.mineral_field.find_by_tag(target_mf_tag)
                if mf:
                    mf.custom_assigned_harvesters += 1
                    cc = self.AI.townhalls.ready.not_flying.closest_to(mf)
                    cc.custom_assigned_harvesters += 1
                    continue

        for refinery in self.AI.gas_buildings.ready:
            refinery.custom_surplus_harvesters = refinery.custom_assigned_harvesters - 3
        for cc in self.AI.townhalls.ready.not_flying:
            mfs_amount = self.AI.mineral_field.closer_than(10, cc).amount
            cc.custom_surplus_harvesters = cc.custom_assigned_harvesters - mfs_amount
        for mf in self.AI.mineral_field:
            mf.custom_surplus_harvesters = mf.custom_assigned_harvesters - 2

        """Send idle scvs to mine minerals"""
        for scv in self.AI.units(UnitTypeId.SCV):
            if scv.is_selected:
                print("For debug only")
            if scv.tag == self.builder_tag:
                continue
            if scv.tag in self.active_builders_tag_list:
                if scv.is_idle:
                    self.active_builders_tag_list.remove(scv.tag)
                elif (
                    scv.is_gathering
                    and scv.orders[0].target
                    in self.AI.structures(UnitTypeId.REFINERY).tags
                ):
                    if scv.tag not in self.vespene_collector_dict:
                        self.active_builders_tag_list.remove(scv.tag)
                        self.vespene_collector_dict[scv.tag] = scv.orders[0].target
                continue
            elif scv.tag in self.mineral_collector_dict:
                """reserved for mineral collector related stuff"""
                continue
            elif scv.tag in self.vespene_collector_dict:
                """reserved for vespene collector related stuff"""
                continue
            elif scv.tag in self.repairer_tag_list:
                """reserved for repairer related stuff"""
                continue
            elif scv.tag in self.boys_tag_list:
                """reserved for BOYS related stuff"""
                continue
            elif scv.tag in self.scout_tag_list:
                if scv.is_idle:
                    loguru.logger.info(f"Scout idle")

                continue
            elif scv.is_idle:
                # print("scv_manager: Idle SCV.")
                await self.remove_unit_tag_from_lists(scv.tag)
                cc = self.AI.townhalls.ready.not_flying.sorted(
                    lambda x: x.distance_to(scv)
                ).first
                mfs = self.AI.mineral_field.closer_than(10, cc)
                mf = mfs.sorted(lambda x: x.custom_assigned_harvesters).first
                self.mineral_collector_dict[scv.tag] = mf.tag
            else:
                print(
                    "scv_manager: Scv has no dedicated group. Assign to mineral collection"
                )
                cc = self.AI.townhalls.ready.not_flying.sorted(
                    lambda x: x.distance_to(scv)
                ).first
                mfs = self.AI.mineral_field.closer_than(10, cc)
                mf = mfs.sorted(lambda x: x.custom_assigned_harvesters).first
                self.mineral_collector_dict[scv.tag] = mf.tag

        """
        # select closes scv to mine gas if needed
        # stop gas miner if too many (will be assigned to minerals in next iteration
        # at some point, differentiate between a 'close' mineral patch and a 'far' one. You always want to grab vesperine miners and builders from the far away patch miners."""
        for refinery in self.AI.gas_buildings.ready:
            if (
                refinery.custom_assigned_harvesters < self.SCVs_PER_REFINERY
                and self.GAS_MINERS_TOTAL < len(self.vespene_collector_dict)
            ):
                scv = await self.select_contractor(position=refinery.position)
                if scv:
                    await self.remove_unit_tag_from_lists(unit_tag=scv.tag)
                    self.vespene_collector_dict[scv.tag] = refinery.tag
                    scv.gather(refinery)
                    break
            if (
                refinery.custom_assigned_harvesters > self.SCVs_PER_REFINERY
                or self.GAS_MINERS_TOTAL > len(self.vespene_collector_dict)
            ):
                scv_to_stop = None
                for scv in self.AI.units(UnitTypeId.SCV):
                    if scv.tag in self.vespene_collector_dict:
                        scv_target_refinery_tag = self.vespene_collector_dict[scv.tag]
                        if scv_target_refinery_tag == refinery.tag:
                            scv_to_stop = scv
                            break
                if scv_to_stop:
                    scv_to_stop.move(scv_to_stop.position)
                    await self.remove_unit_tag_from_lists(scv_to_stop.tag)
                    break

            cc_with_excess_workers = None
            for cc in self.AI.townhalls:
                if cc.custom_surplus_harvesters > 1:
                    cc_with_excess_workers = cc
                    break
            if cc_with_excess_workers:
                for cc in self.AI.townhalls.sorted(lambda x: x.distance_to(scv)):
                    if cc.custom_surplus_harvesters < 0:
                        scv = await self.select_contractor(
                            position=cc_with_excess_workers.position
                        )
                        mf = (
                            self.AI.mineral_field.closer_than(10, cc)
                            .sorted(lambda x: x.custom_surplus_harvesters)
                            .first
                        )
                        scv.gather(mf)
                        self.mineral_collector_dict[scv.tag] = mf.tag
                        break

        for scv in self.AI.units(UnitTypeId.SCV):
            if scv.is_selected:
                print("For debug only")
            if scv.tag in self.mineral_collector_dict:
                target_mineralfield_tag = self.mineral_collector_dict[scv.tag]
                self.SCVManagerUtil.speed_mine_minerals_single(
                    SCV=scv,
                    target_mineral_field_tag=target_mineralfield_tag,
                    mineral_collector_dict=self.mineral_collector_dict,
                )
            elif scv.tag in self.vespene_collector_dict:
                target_refinery_tag = self.vespene_collector_dict[scv.tag]
                await self.speed_mine_gas_single(
                    scv=scv, target_refinery_tag=target_refinery_tag
                )

    async def remove_unit_tag_from_lists(self, unit_tag: int) -> None:
        if unit_tag in self.mineral_collector_dict:
            del self.mineral_collector_dict[unit_tag]
        if unit_tag in self.repairer_tag_list:
            self.repairer_tag_list.remove(unit_tag)
        if unit_tag in self.scout_tag_list:
            self.scout_tag_list.remove(unit_tag)
        if unit_tag in self.boys_tag_list:
            self.boys_tag_list.remove(unit_tag)
        if unit_tag in self.active_builders_tag_list:
            self.active_builders_tag_list.remove(unit_tag)
        if unit_tag in self.vespene_collector_dict:
            del self.vespene_collector_dict[unit_tag]
        if unit_tag == self.builder_tag:
            self.builder_tag = 0

    async def speed_mine_gas_single(self, scv: Unit, target_refinery_tag: int):
        transition_distance = 1.8
        min_distance = 0.4
        if scv.is_carrying_resource:
            if len(scv.orders) < 2:
                target = self.AI.townhalls.ready.closest_to(scv)
                if (
                    scv.distance_to(target)
                    < transition_distance + target.radius + scv.radius
                ):
                    if (
                        scv.distance_to(target)
                        < min_distance + target.radius + scv.radius
                    ):
                        scv(AbilityId.SMART, target, queue=False)
                        return
                    waypoint = target.position.towards(scv, target.radius + scv.radius)
                    scv.move(waypoint)
                    scv(AbilityId.SMART, target, queue=True)
            return
        else:
            target = self.AI.gas_buildings.find_by_tag(tag=target_refinery_tag)
            if scv.is_idle and target:
                scv.gather(target)
                return
            if len(scv.orders) < 2:
                if target:
                    if (
                        min_distance + target.radius + scv.radius
                        < scv.distance_to(target)
                        < transition_distance + target.radius + scv.radius
                    ):
                        waypoint = target.position.towards(
                            scv, target.radius + scv.radius
                        )
                        scv.move(waypoint)
                        scv(AbilityId.SMART, target, queue=True)
                return
