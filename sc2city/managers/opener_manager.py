from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId


class OpenerManager:
    def __init__(self, ai=None):
        self.AI = ai
        self.opener_active = True
        self.build_order = []
        self.create_opener = True
        self.corner_depot_positions = None
        self.builder_tag = None
        self.send_scv_scout = True

    def manager_is_active(self):
        return self.opener_active

    async def run_opener(self, opening_strategy=1):
        if self.send_scv_scout and self.AI.time >= 37:
            self.send_scv_scout = False
            await self.AI.scout_manager.create_scouting_grid_for_enemy_main()
            scv = await self.AI.scv_manager.select_contractor(self.AI.start_location)
            if scv:
                await self.AI.scout_manager.assign_unit_tag_scout(scv.tag)

        """[UnitTypeId]"""
        if self.create_opener:
            """Overwrite for opening strategies, @line 21"""
            # opening_strategy = 0
            self.create_opener = False
            if opening_strategy == 0:
                self.build_order = [
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.REFINERY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.COMMANDCENTER,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.COMMANDCENTER,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORY,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSTECHLAB,
                    AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
                    UnitTypeId.BARRACKS,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.STARPORT,
                    UnitTypeId.FACTORYTECHLAB,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.STARPORT,
                    UnitTypeId.SCV,
                    UnitTypeId.BARRACKSREACTOR,
                    UnitTypeId.SCV,
                    UnitTypeId.FACTORYREACTOR,
                    UnitTypeId.SCV,
                    UnitTypeId.STARPORTTECHLAB,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.COMMANDCENTER,
                    UnitTypeId.ENGINEERINGBAY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.STARPORTREACTOR,
                    UnitTypeId.SCV,
                    UnitTypeId.ARMORY,
                    UnitTypeId.BUNKER,
                    UnitTypeId.GHOSTACADEMY,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.MISSILETURRET,
                    UnitTypeId.FUSIONCORE,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SENSORTOWER,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SUPPLYDEPOT,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                    UnitTypeId.SCV,
                ]
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
        if not await self.AI.scv_manager.building_queue_empty():
            return
        next_to_be_build = self.build_order[0]
        if next_to_be_build == "scvs_per_refinery_0":
            self.AI.scv_manager.scvs_per_refinery = 0
            self.build_order.pop(0)
            return
        if next_to_be_build == "scvs_per_refinery_1":
            self.AI.scv_manager.scvs_per_refinery = 1
            self.build_order.pop(0)
            return
        if next_to_be_build == "scvs_per_refinery_2":
            self.AI.scv_manager.scvs_per_refinery = 2
            self.build_order.pop(0)
            return
        if next_to_be_build == "scvs_per_refinery_3":
            self.AI.scv_manager.scvs_per_refinery = 3
            self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.SCV:
            if self.AI.can_afford(next_to_be_build):
                for cc in self.AI.townhalls.ready:
                    if (
                        cc.is_active
                        and cc.orders[0].ability.id
                        == AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND
                    ):
                        continue
                    cc.train(UnitTypeId.SCV)
                    self.build_order.pop(0)
                    return
            return
        if next_to_be_build == UnitTypeId.MARINE:
            if self.AI.can_afford(next_to_be_build):
                for addon in self.AI.structures(UnitTypeId.BARRACKSREACTOR).ready:
                    rax = self.AI.structures(UnitTypeId.BARRACKS).closest_to(
                        addon.add_on_land_position
                    )
                    if len(rax.orders) < 3:
                        rax.train(UnitTypeId.MARINE)
                        self.build_order.pop(0)
                        return
                for addon in self.AI.structures(UnitTypeId.BARRACKSTECHLAB).ready:
                    rax = self.AI.structures(UnitTypeId.BARRACKS).closest_to(
                        addon.add_on_land_position
                    )
                    if len(rax.orders) < 1:
                        rax.train(UnitTypeId.MARINE)
                        self.build_order.pop(0)
                        return
                for rax in self.AI.structures(UnitTypeId.BARRACKS).ready:
                    if len(rax.orders) < 1:
                        rax.train(next_to_be_build)
                        self.build_order.pop(0)
                        return
                print("Opener_manager: No raxes for marine production available!")
            return
        if next_to_be_build == UnitTypeId.MARAUDER:
            if self.AI.can_afford(next_to_be_build):
                for addon in self.AI.structures(UnitTypeId.BARRACKSTECHLAB).ready:
                    rax = self.AI.structures(UnitTypeId.BARRACKS).closest_to(
                        addon.add_on_land_position
                    )
                    if len(rax.orders) < 1:
                        rax.train(next_to_be_build)
                        self.build_order.pop(0)
                        return
                print(
                    "Opener_manager: No raxes with techlabs for marauder production available!"
                )
            return

        if next_to_be_build == UnitTypeId.SUPPLYDEPOT:
            if self.AI.minerals > 30:
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build in [UnitTypeId.BARRACKS, UnitTypeId.ENGINEERINGBAY]:
            if (
                self.AI.minerals > 60
                and self.AI.structures(
                    [UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED]
                ).ready
            ):
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build in [UnitTypeId.ARMORY]:
            if (
                self.AI.minerals > 60
                and self.AI.vespene > 60
                and self.AI.structures(
                    [UnitTypeId.FACTORY]
                ).ready
            ):
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build in [UnitTypeId.SENSORTOWER, UnitTypeId.MISSILETURRET]:
            if (
                self.AI.minerals > 50
                and self.AI.structures(
                    [UnitTypeId.ENGINEERINGBAY]
                ).ready
            ):
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.FACTORY:
            if (
                self.AI.minerals > 60
                and self.AI.vespene > 60
                and (
                    self.AI.structures(UnitTypeId.BARRACKS).ready
                    or self.AI.structures(UnitTypeId.BARRACKSFLYING)
                )
            ):
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.GHOSTACADEMY:
            if (
                self.AI.minerals > 60
                and (
                    self.AI.structures(UnitTypeId.BARRACKS).ready
                    or self.AI.structures(UnitTypeId.BARRACKSFLYING)
                )
            ):
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.FUSIONCORE:
            if (
                self.AI.minerals > 60
                and self.AI.vespene > 100
                and (
                    self.AI.structures(UnitTypeId.STARPORT).ready
                    or self.AI.structures(UnitTypeId.STARPORTFLYING)
                )
            ):
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.BUNKER:
            if (
                self.AI.minerals > 50
                and (
                    self.AI.structures(UnitTypeId.BARRACKS).ready
                    or self.AI.structures(UnitTypeId.BARRACKSFLYING)
                )
            ):
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build == UnitTypeId.STARPORT:
            if (
                self.AI.minerals > 60
                and self.AI.vespene > 60
                and (
                    self.AI.structures(
                        [UnitTypeId.FACTORY, UnitTypeId.FACTORYFLYING]
                    ).ready
                    or self.AI.structures(UnitTypeId.BARRACKSFLYING)
                )
            ):
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        if next_to_be_build in [UnitTypeId.BARRACKSREACTOR, UnitTypeId.BARRACKSTECHLAB]:
            if self.AI.can_afford(next_to_be_build):
                for rax in self.AI.structures(UnitTypeId.BARRACKS).ready.idle:
                    if not rax.add_on_tag:
                        rax.build(next_to_be_build)
                        self.build_order.pop(0)
                        return
                print("Opener_manager: No raxes without add_ons available!")
            return
        if next_to_be_build in [UnitTypeId.FACTORYREACTOR, UnitTypeId.FACTORYTECHLAB]:
            if self.AI.can_afford(next_to_be_build):
                for rax in self.AI.structures(UnitTypeId.FACTORY).ready.idle:
                    if not rax.add_on_tag:
                        rax.build(next_to_be_build)
                        self.build_order.pop(0)
                        return
                print("Opener_manager: No factories without add_ons available!")
            return
        if next_to_be_build in [UnitTypeId.STARPORTREACTOR, UnitTypeId.STARPORTTECHLAB]:
            if self.AI.can_afford(next_to_be_build):
                for rax in self.AI.structures(UnitTypeId.STARPORT).ready.idle:
                    if not rax.add_on_tag:
                        rax.build(next_to_be_build)
                        self.build_order.pop(0)
                        return
                print("Opener_manager: No starports without add_ons available!")
            return
        if next_to_be_build == UnitTypeId.REFINERY:
            await self.AI.scv_manager.queue_building(structure_type_id=next_to_be_build)
            self.build_order.pop(0)
            return
        if next_to_be_build == AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND:
            if self.AI.can_afford(next_to_be_build) and (
                self.AI.structures(UnitTypeId.BARRACKS).ready
                or self.AI.structures(UnitTypeId.BARRACKSFLYING)
            ):
                for cc in self.AI.townhalls(UnitTypeId.COMMANDCENTER).ready.idle:
                    cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
                    self.build_order.pop(0)
                    return
            return
        if next_to_be_build == AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS:
            if self.AI.can_afford(next_to_be_build) and (
                self.AI.structures(UnitTypeId.ENGINEERINGBAY).ready
            ):
                for cc in self.AI.townhalls(UnitTypeId.COMMANDCENTER).ready.idle:
                    cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
                    self.build_order.pop(0)
                    return
            return
        if next_to_be_build in [
            AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK,
            AbilityId.RESEARCH_COMBATSHIELD,
        ]:
            for facility in self.AI.structures(UnitTypeId.BARRACKSTECHLAB).ready.idle:
                if self.AI.can_afford(next_to_be_build):
                    print("Upgrade: " + str(next_to_be_build))
                    facility(next_to_be_build)
                    self.build_order.pop(0)
                print("No idle BARRACKSTECHLAB available!")
            return
        if next_to_be_build in [
            AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1
        ]:
            for facility in self.AI.structures(UnitTypeId.ENGINEERINGBAY).ready.idle:
                if self.AI.can_afford(next_to_be_build):
                    print("Upgrade: " + str(next_to_be_build))
                    facility(next_to_be_build)
                    self.build_order.pop(0)
                print("No idle ENGINEERINGBAY available!")
            return
        if next_to_be_build == UnitTypeId.COMMANDCENTER:
            if self.AI.minerals > 250:
                await self.AI.scv_manager.queue_building(
                    structure_type_id=next_to_be_build
                )
                self.build_order.pop(0)
            return
        print("Opener_manager: Unknown " + str(next_to_be_build))
