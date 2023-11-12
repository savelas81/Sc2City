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
        self.next_building_type = None
        self.next_building_position = Point2((0, 0))

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

        """choice scv"""
        """send this scv to building location"""
        """once enough money build the building"""
        pass