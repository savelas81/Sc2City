import typing

import loguru
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union
import math


async def get_mining_positions(mineral_field: Unit) -> List[Point2]:
    scv_radius = 0.375
    p = Point2(mineral_field.position)
    return [
        Point2((p.x - 0.5, p.y - (0.5 + scv_radius))),
        Point2((p.x - 0.5, p.y + (0.5 + scv_radius))),
        Point2((p.x + 0.5, p.y - (0.5 + scv_radius))),
        Point2((p.x + 0.5, p.y + (0.5 + scv_radius))),
        Point2((p.x - (1 + scv_radius), p.y)),
        Point2((p.x - (1 + scv_radius), p.y - (0.5 + scv_radius))),
        Point2((p.x - (1 + scv_radius), p.y + (0.5 + scv_radius))),
        Point2((p.x + (1 + scv_radius), p.y)),
        Point2((p.x + (1 + scv_radius), p.y - (0.5 + scv_radius))),
        Point2((p.x + (1 + scv_radius), p.y + (0.5 + scv_radius))),
    ]


class ScvManager:
    def __init__(self, AI: BotAI = None):
        # Miscellaneous:
        self.AI: BotAI = AI
        self.mineral_collector_dict = {}
        self.vespene_collector_dict = {}
        self.repairer_tag_list = []
        self.boys_tag_list = []
        self.builder_tag: int = 0
        self.scout_tag_list = []
        self.active_builders_tag_list = []
        self.next_building_type = None
        self.next_building_position = Point2((0, 0))
        self.remember_first_builder = True
        self.first_builder_tag: int = 0
        self.expand_to_natural = True
        self.scvs_per_refinery = 3  # valid values 0-3

    async def worker_split_frame_zero(self):
        self.expand_to_natural = await self.AI.get_next_expansion()
        mfs = self.AI.mineral_field.closer_than(10, self.AI.townhalls.first.position)
        workers = self.AI.units(UnitTypeId.SCV)
        for mf in mfs:  # type: Unit
            if workers:
                worker = workers.closest_to(mf)
                worker.gather(mf)
                self.mineral_collector_dict[worker.tag] = mf.tag
                workers.remove(worker)
        for worker in workers:  # type: Unit
            mf = mfs.closest_to(worker)
            worker.gather(mf)
            self.mineral_collector_dict[worker.tag] = mf.tag

    async def building_queue_empty(self) -> bool:
        if self.next_building_type is None:
            return True
        else:
            return False

    async def queue_building(self, structure_type_id=UnitTypeId.BARRACKS):
        print("scv_manager: queue building: " + str(structure_type_id))
        if structure_type_id == UnitTypeId.REFINERY:
            self.next_building_type = structure_type_id
            return
        position = await self.AI.building_placements.get_placement_for(
            structure_type_id=structure_type_id
        )
        if position is None:
            loguru.logger.info(
                f"Position is None for some reason..... Structure Type ID: {str(structure_type_id)}"
            )
            return
        else:
            if self.expand_to_natural and structure_type_id == UnitTypeId.COMMANDCENTER:
                position = self.expand_to_natural
                self.expand_to_natural = False
            if self.first_builder_tag != 0:
                contractor = self.first_builder_tag
                self.first_builder_tag = 0
            else:
                contractor = await self.select_contractor(position=position)
            if self.remember_first_builder:
                self.first_builder_tag = contractor
                self.remember_first_builder = False
            if not contractor:
                print("scv_manager: No builder selected!")
                return
            await self.remove_unit_tag_from_lists(contractor.tag)
            self.builder_tag = contractor.tag
            self.next_building_type = structure_type_id
            self.next_building_position = Point2(position)
            contractor.move(self.next_building_position)

    async def select_contractor(self, position: Point2) -> Optional[Unit]:
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
        await self.distribute_workers()
        await self.build_queued_building()

    async def add_unit_tag_scout_list(self, unit_tag: int):
        await self.remove_unit_tag_from_lists(unit_tag=unit_tag)
        self.scout_tag_list.append(unit_tag)

    async def build_queued_building(self):
        if await self.building_queue_empty():
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
                            print("Scv building "
                                  + str(self.next_building_type)
                                  + " at time "
                                  + str(self.AI.time_formatted)
                                  + " minerals "
                                  + str(self.AI.minerals)
                                  + " vespene "
                                  + str(self.AI.vespene))
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
                        print("Scv building "
                              + str(self.next_building_type)
                              + " at time "
                              + str(self.AI.time_formatted)
                              + " minerals "
                              + str(self.AI.minerals)
                              + " vespene "
                              + str(self.AI.vespene))
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
                """reserved for scout related stuff"""
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
                print("scv_manager: Scv has no dedicated group. Assign to mineral collection")
                cc = self.AI.townhalls.ready.not_flying.sorted(
                    lambda x: x.distance_to(scv)
                ).first
                mfs = self.AI.mineral_field.closer_than(10, cc)
                mf = mfs.sorted(lambda x: x.custom_assigned_harvesters).first
                self.mineral_collector_dict[scv.tag] = mf.tag

        """select closes scv to mine gas if needed"""
        """stop gas miner if too many (will be assigned to minerals in next iteration"""
        if self.AI.iteration % 4 == 0:
            for refinery in self.AI.gas_buildings.ready:
                if refinery.custom_assigned_harvesters < self.scvs_per_refinery:
                    scv = await self.select_contractor(position=refinery.position)
                    if scv:
                        await self.remove_unit_tag_from_lists(unit_tag=scv.tag)
                        self.vespene_collector_dict[scv.tag] = refinery.tag
                        scv.gather(refinery)
                        break
                if refinery.custom_assigned_harvesters > self.scvs_per_refinery:
                    scv_to_stop = None
                    for scv in self.AI.units(UnitTypeId.SCV):
                        if scv.tag in self.vespene_collector_dict:
                            scv_target_refinery_tag = self.vespene_collector_dict[
                                scv.tag
                            ]
                            if scv_target_refinery_tag == refinery.tag:
                                scv_to_stop = scv
                                break
                    if scv_to_stop:
                        scv_to_stop.move(scv_to_stop.position)
                        await self.remove_unit_tag_from_lists(scv_to_stop.tag)
                        break

            cc_with_excess_workers: Unit = Unit([], self.AI)
            for cc in self.AI.townhalls:
                if cc.custom_surplus_harvesters > 1:
                    cc_with_excess_workers = cc
                    break
            if cc_with_excess_workers:
                for cc in self.AI.townhalls.sorted(lambda x: x.distance_to(scv)):
                    if cc.custom_surplus_harvesters < 0:
                        scv = await self.select_contractor(position=cc_with_excess_workers.position)
                        mf = self.AI.mineral_field.closer_than(10, cc).sorted(lambda x: x.custom_surplus_harvesters).first
                        scv.gather(mf)
                        self.mineral_collector_dict[scv.tag] = mf.tag
                        break

        for scv in self.AI.units(UnitTypeId.SCV):
            if scv.is_selected:
                print("For debug only")
            if scv.tag in self.mineral_collector_dict:
                target_mineralfield_tag = self.mineral_collector_dict[scv.tag]
                await self.speed_mine_minerals_single(
                    scv=scv, target_mineralfield_tag=target_mineralfield_tag
                )
            elif scv.tag in self.vespene_collector_dict:
                target_refinery_tag = self.vespene_collector_dict[scv.tag]
                await self.speed_mine_gas_single(
                    scv=scv, target_refinery_tag=target_refinery_tag
                )

    async def remove_unit_tag_from_lists(self, unit_tag: int):
        if unit_tag in self.mineral_collector_dict:
            self.mineral_collector_dict.pop(unit_tag)
        if unit_tag in self.repairer_tag_list:
            self.repairer_tag_list.remove(unit_tag)
        if unit_tag in self.scout_tag_list:
            self.scout_tag_list.remove(unit_tag)
        if unit_tag in self.boys_tag_list:
            self.boys_tag_list.remove(unit_tag)
        if unit_tag in self.active_builders_tag_list:
            self.active_builders_tag_list.remove(unit_tag)
        if unit_tag in self.vespene_collector_dict:
            self.vespene_collector_dict.pop(unit_tag)
        if unit_tag == self.builder_tag:
            self.builder_tag = 0

    async def speed_mine_minerals_single(self, scv: Unit, target_mineralfield_tag: int):
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
            target = self.AI.mineral_field.find_by_tag(tag=target_mineralfield_tag)
            if scv.is_idle and target:
                scv.gather(target)
                return
            if len(scv.orders) < 2:
                if target:
                    if len(scv.orders) == 1 and scv.orders[0].target != target.tag:
                        if scv.orders[0].target not in self.AI.mineral_field.tags:
                            print("scv_manager: scv has invalid target ID")
                            scv.gather(target)
                        else:
                            self.mineral_collector_dict[scv.tag] = scv.orders[0].target
                        return
                    if (
                        min_distance + target.radius + scv.radius
                        < scv.distance_to(target)
                        < transition_distance + target.radius + scv.radius
                    ):
                        mining_positions = await get_mining_positions(
                            mineral_field=target
                        )
                        closest = Point2((0, 0))
                        min_dist = math.inf
                        for pos in mining_positions:
                            if not self.AI.in_pathing_grid(pos):
                                continue
                            dist = pos.distance_to(scv)
                            if dist < min_dist:
                                min_dist = dist
                                closest = pos
                        if closest != Point2((0, 0)):
                            waypoint = closest
                            scv.move(waypoint)
                            scv(AbilityId.SMART, target, queue=True)
                return

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
