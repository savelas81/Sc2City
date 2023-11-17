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

    async def run_opener(self, opening_strategy=1):
        """[UnitTypeId]"""
        if self.create_opener:
            self.create_opener = False
            if opening_strategy == 1:
                self.build_order = [
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.COMMANDCENTER,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.COMMANDCENTER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.FACTORYTECHLAB,
                ]
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
        if len(self.build_order) == 0:
            self.opener_active = False
            print("Opener_manager: Opener completed.")
            return
        if not await self.ai.scv_manager.building_queue_empty():
            return
        next_to_be_build = self.build_order[0]
        if next_to_be_build == "add_vespene":
            self.ai.scv_manager.target_vespene_collectors += 1
            self.build_order.pop(0)
            return
        if next_to_be_build == "remove_vespene":
            self.ai.scv_manager.target_vespene_collectors -= 1
            self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.SCV:
            if self.ai.can_afford(next_to_be_build):
                for cc in self.ai.townhalls.ready:
                    if cc.is_active and cc.orders[0].ability.id == AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND:
                        continue
                    cc.train(UnitTypeId.SCV)
                    self.build_order.pop(0)
                    return
            return
        if next_to_be_build == UnitTypeId.MARINE:
            if self.ai.can_afford(next_to_be_build):
                for addon in self.ai.structures(UnitTypeId.BARRACKSREACTOR).ready:
                    rax = self.ai.structures(UnitTypeId.BARRACKS).closest_to(addon.add_on_land_position)
                    if len(rax.orders) < 3:
                        rax.train(UnitTypeId.MARINE)
                        self.build_order.pop(0)
                        return
                for addon in self.ai.structures(UnitTypeId.BARRACKSTECHLAB).ready:
                    rax = self.ai.structures(UnitTypeId.BARRACKS).closest_to(addon.add_on_land_position)
                    if len(rax.orders) < 2:
                        rax.train(UnitTypeId.MARINE)
                        self.build_order.pop(0)
                        return
                for rax in self.ai.structures(UnitTypeId.BARRACKS).ready:
                    if len(rax.orders) < 2:
                        rax.train(UnitTypeId.MARINE)
                        self.build_order.pop(0)
                        return
            return
        if next_to_be_build == UnitTypeId.SUPPLYDEPOT:
            if self.ai.minerals > 30:
                await self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)
                self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.BARRACKS:
            if self.ai.minerals > 60 and self.ai.structures(UnitTypeId.SUPPLYDEPOT).ready:
                await self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)
                self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.FACTORY:
            if (self.ai.minerals > 60
                    and self.ai.vespene > 60
                    and (self.ai.structures(UnitTypeId.SUPPLYDEPOT).ready
                         or self.ai.structures(UnitTypeId.BARRACKSFLYING))):
                await self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)
                self.build_order.pop(0)
            return
        if next_to_be_build in [UnitTypeId.BARRACKSREACTOR, UnitTypeId.BARRACKSTECHLAB]:
            if self.ai.can_afford(next_to_be_build):
                for rax in self.ai.structures(UnitTypeId.BARRACKS).ready.idle:
                    if not rax.add_on_tag:
                        rax.build(next_to_be_build)
                        self.build_order.pop(0)
                        return
                print("Opener_manager: No raxes without add_ons available!")
            return
        if next_to_be_build in [UnitTypeId.FACTORYREACTOR, UnitTypeId.FACTORYTECHLAB]:
            if self.ai.can_afford(next_to_be_build):
                for rax in self.ai.structures(UnitTypeId.FACTORY).ready.idle:
                    if not rax.add_on_tag:
                        rax.build(next_to_be_build)
                        self.build_order.pop(0)
                        return
                print("Opener_manager: No factories without add_ons available!")
            return
        if next_to_be_build == UnitTypeId.REFINERY:
            await self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)
            self.build_order.pop(0)
            return
        if next_to_be_build == AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND:
            for cc in self.ai.townhalls(UnitTypeId.COMMANDCENTER).ready.idle:
                cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
                self.build_order.pop(0)
                return
            return
        if next_to_be_build == UnitTypeId.COMMANDCENTER:
            if self.ai.minerals > 250:
                await self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)
                self.build_order.pop(0)
            return
        print("Opener_manager: Unknown " + str(next_to_be_build))

