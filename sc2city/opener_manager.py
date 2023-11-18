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
            """Overwrite for opening strategies, @line 21"""
            opening_strategy = 4
            self.create_opener = False
            if opening_strategy == 1:
                self.build_order = [
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.COMMANDCENTER,
                    UnitTypeId.SCV,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.COMMANDCENTER,
                    UnitTypeId.SCV,
                    UnitTypeId.REFINERY,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSTECHLAB,
                    UnitTypeId.SCV,
                    AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.BARRACKSTECHLAB,
                    UnitTypeId.SCV,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.SCV,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    AbilityId.RESEARCH_COMBATSHIELD,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSREACTOR,
                    UnitTypeId.SCV,
                    UnitTypeId.REFINERY,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORY,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSREACTOR,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.STARPORT,
                    UnitTypeId.FACTORYREACTOR,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.BUNKER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.ENGINEERINGBAY,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORYTECHLAB,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MISSILETURRET,
                    UnitTypeId.SIEGETANK,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MISSILETURRET,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MISSILETURRET,
                    UnitTypeId.MISSILETURRET,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1,
                ]
            if opening_strategy == 2:
                self.build_order = [
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.COMMANDCENTER,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.REFINERY,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSTECHLAB,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORY,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.SCV,
                    AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSTECHLAB,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    AbilityId.RESEARCH_COMBATSHIELD,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.BARRACKSREACTOR,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.ENGINEERINGBAY,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.MARAUDER,
                    AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1,
                    UnitTypeId.MISSILETURRET,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MISSILETURRET,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.STARPORT,
                    UnitTypeId.FACTORYREACTOR,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.BARRACKSREACTOR,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARINE,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MEDIVAC,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                ]
            if opening_strategy == 3:
                self.build_order = [
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.COMMANDCENTER,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.REFINERY,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.BARRACKSREACTOR,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORY,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSTECHLAB,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORYTECHLAB,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SIEGETANK,
                    UnitTypeId.MARAUDER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MARINE,
                    UnitTypeId.MARINE,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                ]
            if opening_strategy == 4:
                self.build_order = [
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.COMMANDCENTER,
                    UnitTypeId.BARRACKSREACTOR,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.REAPER,
                    UnitTypeId.REAPER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.REAPER,
                    UnitTypeId.REAPER,
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
        if next_to_be_build == "scvs_per_refinery_0":
            self.ai.scv_manager.scvs_per_refinery = 0
            self.build_order.pop(0)
            return
        if next_to_be_build == "scvs_per_refinery_1":
            self.ai.scv_manager.scvs_per_refinery = 1
            self.build_order.pop(0)
            return
        if next_to_be_build == "scvs_per_refinery_2":
            self.ai.scv_manager.scvs_per_refinery = 2
            self.build_order.pop(0)
            return
        if next_to_be_build == "scvs_per_refinery_3":
            self.ai.scv_manager.scvs_per_refinery = 3
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
                    if len(rax.orders) < 1:
                        rax.train(UnitTypeId.MARINE)
                        self.build_order.pop(0)
                        return
                for rax in self.ai.structures(UnitTypeId.BARRACKS).ready:
                    if len(rax.orders) < 1:
                        rax.train(next_to_be_build)
                        self.build_order.pop(0)
                        return
            print("Opener_manager: No raxes for marine production available!")
            return
        if next_to_be_build == UnitTypeId.MARAUDER:
            if self.ai.can_afford(next_to_be_build):
                for addon in self.ai.structures(UnitTypeId.BARRACKSTECHLAB).ready:
                    rax = self.ai.structures(UnitTypeId.BARRACKS).closest_to(addon.add_on_land_position)
                    if len(rax.orders) < 1:
                        rax.train(next_to_be_build)
                        self.build_order.pop(0)
                        return
            print("Opener_manager: No raxes with techlabs for marauder production available!")
            return

        if next_to_be_build == UnitTypeId.SUPPLYDEPOT:
            if self.ai.minerals > 30:
                await self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)
                self.build_order.pop(0)
            return
        if next_to_be_build in [UnitTypeId.BARRACKS, UnitTypeId.ENGINEERINGBAY]:
            if self.ai.minerals > 60 and self.ai.structures([UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED]).ready:
                await self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)
                self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.FACTORY:
            if (self.ai.minerals > 60
                    and self.ai.vespene > 60
                    and (self.ai.structures(UnitTypeId.BARRACKS).ready
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
        if next_to_be_build in [AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK, AbilityId.RESEARCH_COMBATSHIELD]:
            for facility in self.ai.structures(UnitTypeId.BARRACKSTECHLAB).ready.idle:
                if self.ai.can_afford(next_to_be_build):
                    print("Upgrade: " + str(next_to_be_build))
                    facility(next_to_be_build)
                    self.build_order.pop(0)
            print("No idle BARRACKSTECHLAB available!")
            return
        if next_to_be_build in [AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1]:
            for facility in self.ai.structures(UnitTypeId.ENGINEERINGBAY).ready.idle:
                if self.ai.can_afford(next_to_be_build):
                    print("Upgrade: " + str(next_to_be_build))
                    facility(next_to_be_build)
                    self.build_order.pop(0)
            print("No idle ENGINEERINGBAY available!")
            return
        if next_to_be_build == UnitTypeId.COMMANDCENTER:
            if self.ai.minerals > 250:
                await self.ai.scv_manager.queue_building(structure_type_id=next_to_be_build)
                self.build_order.pop(0)
            return
        print("Opener_manager: Unknown " + str(next_to_be_build))

