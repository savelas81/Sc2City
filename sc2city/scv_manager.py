from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.position import Point2
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union


class ScvManager:

    def __init__(self, ai=None):
        self.ai = ai
        self.mineral_collector_dict = {}
        self.vespene_collector_dict = {}
        self.repairer_tag_list = []
        self.boys_tag_list = []
        self.builder_tag: int = 0
        self.active_builders_tag_list = []
        self.next_building_type = None
        self.next_building_position = Point2((0, 0))
        self.remember_first_builder = True
        self.first_builder_tag: int = 0
        self.expand_to_natural = True
        self.scvs_per_refinery = 3  # valid values 0, 2, 3
        self.target_vespene_collectors = 0

    async def worker_spit_frame_zero(self):
        self.expand_to_natural = await self.ai.get_next_expansion()
        mfs = self.ai.mineral_field.closer_than(10, self.ai.townhalls.first.position)
        workers = self.ai.units(UnitTypeId.SCV)
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
        if structure_type_id == UnitTypeId.REFINERY:
            self.next_building_type = structure_type_id
            return
        position = await self.ai.building_placements.get_placement_for(structure_type_id=structure_type_id)
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
        if contractor.tag in self.mineral_collector_dict:
            self.mineral_collector_dict.pop(contractor.tag)
        self.builder_tag = contractor.tag
        self.next_building_type = structure_type_id
        self.next_building_position = Point2(position)
        contractor.move(self.next_building_position)

    async def select_contractor(self, position: Point2) -> Optional[Unit]:
        if not position:
            print("scv_manager: No position for building!")
            return None
        scvs = self.ai.units(UnitTypeId.SCV)
        for scv in scvs:
            # TODO select closest by pathing. Now it is basically random
            if scv.tag not in self.mineral_collector_dict:
                continue
            else:
                return scv
        print("scv_manager: No valid scv for builder!")
        return None

    async def move_scvs(self):
        await self.distribute_workers()
        await self.build_queued_building()
        # await self.mine_minerals()
        # await self.mine_gas()

    async def build_queued_building(self):
        if await self.building_queue_empty():
            return
        if self.next_building_type == UnitTypeId.REFINERY:
            if self.ai.can_afford(self.next_building_type):
                for cc in self.ai.townhalls:
                    geysers = self.ai.vespene_geyser.closer_than(10.0, cc)
                    for geyser in geysers:
                        point = geyser.position.towards(self.ai.game_info.map_center, 2)
                        if not self.ai.gas_buildings.closer_than(1.0, geyser):
                            contractor = await self.select_contractor(position=point)
                            if contractor is None:
                                return
                            contractor.build(UnitTypeId.REFINERY, geyser)
                            if contractor.tag in self.mineral_collector_dict.keys:
                                self.mineral_collector_dict.pop(contractor.tag)
                            if contractor.tag not in self.active_builders_tag_list:
                                self.active_builders_tag_list.append(contractor.tag)
                            self.next_building_type = None
                            return
        else:
            if self.ai.can_afford(self.next_building_type):
                for scv in self.ai.units(UnitTypeId.SCV):
                    if scv.tag == self.builder_tag:
                        scv.build(self.next_building_type, self.next_building_position)
                        if self.builder_tag not in self.active_builders_tag_list:
                            self.active_builders_tag_list.append(self.builder_tag)
                        self.builder_tag: int = 0
                        self.next_building_type = None
                        self.next_building_position = Point2((0, 0))
                        return
                print("scv_manager: No scv tags match self.builder_tag")
                return

    async def distribute_workers(self):
        """Send idle scvs to mine minerals
           select closes scv to mine gas if needed
           stop gas miner if too many (will be assigned to minerals in next iteration"""
        for structure in (self.ai.gas_buildings | self.ai.townhalls | self.ai.mineral_field):
            structure.custom_assigned_harvesters = 0
        for scv in self.ai.units(UnitTypeId.SCV):
            if scv.tag in self.vespene_collector_dict.keys():
                target_refinery_tag = self.vespene_collector_dict[scv.tag]
                for refinery in self.ai.gas_buildings.ready:
                    if refinery.tag == target_refinery_tag:
                        refinery.custom_assigned_harvesters += 1
                        break
            elif scv.tag in self.mineral_collector_dict.keys():
                target_mf_tag = self.mineral_collector_dict[scv.tag]
                for mf in self.ai.mineral_field:
                    if mf.tag == target_mf_tag:
                        mf.custom_assigned_harvesters += 1
                        cc = self.ai.townhalls.ready.not_flying.closest_to(mf)
                        cc.custom_assigned_harvesters += 1
                        break
            elif scv.is_idle:
                print("scv_manager: Idle SCV.")

        if self.ai.opener_manager.opener_is_active:
            if len(self.vespene_collector_dict) < self.target_vespene_collectors:
                pass
        else:
            # TODO saturate gas buildings based on self.scvs_per_refinery
            pass

    async def remove_unit_tag_from_lists(self, unit_tag: int):
        if unit_tag in self.mineral_collector_dict.keys:
            self.mineral_collector_dict.pop(unit_tag)
        if unit_tag in self.repairer_tag_list:
            self.repairer_tag_list.remove(unit_tag)
        if unit_tag in self.boys_tag_list:
            self.boys_tag_list.remove(unit_tag)
        if unit_tag in self.active_builders_tag_list:
            self.active_builders_tag_list.remove(unit_tag)
        if unit_tag in self.vespene_collector_dict.keys():
            self.vespene_collector_dict.pop(unit_tag)
        if unit_tag == self.builder_tag:
            self.builder_tag = 0

    async def mine_minerals_single(self):
        pass

    async def mine_gas_single(self):
        pass
