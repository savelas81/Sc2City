from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId


class OpenerManager:
    def __init__(self, ai=None):
        self.ai = ai
        self.opener_active = True
        self.build_order = []
        self.create_opener = True
        self.corner_depot_positions = None
        self.builder_tag = None

    def opener_is_active(self):
        return self.opener_active

    def run_opener(self, opening_strategy=1):
        """[UnitTypeId]"""
        if self.create_opener:
            self.create_opener = False
            if opening_strategy == 1:
                self.build_order = []
            if opening_strategy == 2:
                self.build_order = []
            if opening_strategy == 3:
                self.build_order = [
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSREACTOR,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.SCV,
                ]
        if not self.ai.scv_manager.building_queue_empty:
            return
        next_to_be_build = self.build_order[0]
        if next_to_be_build == UnitTypeId.SCV:
            if self.ai.can_afford(next_to_be_build):
                for cc in self.ai.townhalls.ready:
                    cc.train(UnitTypeId.SCV)
                    self.build_order.pop(0)
                return
        if next_to_be_build == UnitTypeId.SUPPLYDEPOT:
            if self.ai.minerals > 50:
                self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)

            else:
                if self.ai.can_afford(next_to_be_build):
                    for position in self.corner_depot_positions:
                        if self.ai.building_placements.this_valid_building_location(position=position):
                            for scv in self.ai.units(UnitTypeId.SCV):
                                if self.builder_tag == scv.tag:
                                    scv.build(next_to_be_build, position)
                                    self.builder_tag = None
                                    self.build_order.pop(0)
                                    # TODO we need to make sure that the building started
                                    # before clearing nex item from build order.




        pass

