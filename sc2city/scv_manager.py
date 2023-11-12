from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.position import Point2


class ScvManager:

    def __init__(self, ai=None):
        self.ai = ai
        self.mineral_collector_tag_list = []
        self.vespene_collector_tag_list = []
        self.repairer_tag_list = []
        self.boys_list = []
        self.builder_tag: int = 0
        self.active_builders_tag_list = []
        self.next_building_type = None
        self.next_building_position = Point2((0, 0))
        self.remember_first_builder = True
        self.first_builder_tag: int = 0

    async def worker_spit_frame_zero(self):
        mfs = self.ai.mineral_field.closer_than(10, self.ai.townhalls.first.position)
        workers = self.ai.units(UnitTypeId.SCV)
        for mf in mfs:  # type: Unit
            if workers:
                worker = workers.closest_to(mf)
                worker.gather(mf)
                self.mineral_collector_tag_list.append(worker.tag)
                workers.remove(worker)
        for worker in workers:  # type: Unit
            worker.gather(mfs.closest_to(worker))
            self.mineral_collector_tag_list.append(worker.tag)

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
        if contractor.tag in self.mineral_collector_tag_list:
            self.mineral_collector_tag_list.remove(contractor.tag)
        self.builder_tag = contractor.tag
        self.next_building_type = structure_type_id
        self.next_building_position = Point2(position)
        contractor.move(self.next_building_position)

    async def select_contractor(self, position: Point2) -> Unit:
        if not position:
            print("scv_manager: No position for building!")
            return None
        scvs = self.ai.units(UnitTypeId.SCV)
        for scv in scvs:
            # TODO select closest by pathing. Now it is basically random
            if scv.tag not in self.mineral_collector_tag_list:
                continue
            else:
                return scv
        print("scv_manager: No valid scv for builder!")
        return None

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
                            if contractor.tag in self.mineral_collector_tag_list:
                                self.mineral_collector_tag_list.remove(contractor.tag)
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



