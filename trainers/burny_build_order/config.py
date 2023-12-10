from dataclasses import dataclass

from sc2.ids.ability_id import AbilityId

from sc2city.utils import OrderType
from sc2city.game_objects import CustomAbilities


@dataclass
class BurnyOrder:
    id: int
    name: str
    type: str
    supply: int
    time: str
    frame: int


BURNY_ACTIONS = {
    "worker_to_mins": CustomAbilities.WORKER_TO_MINS.name,
    "worker_to_gas": CustomAbilities.WORKER_TO_GAS.name,
    "3worker_to_gas": CustomAbilities.WORKER_TO_GAS_3.name,
    "worker_to_scout": CustomAbilities.WORKER_TO_SCOUT.name,
    "worker_from_scout": CustomAbilities.WORKER_FROM_SCOUT.name,
    "do_nothing_1_sec": CustomAbilities.DO_NOTHING_1_SEC.name,
    "do_nothing_5_sec": CustomAbilities.DO_NOTHING_5_SEC.name,
    "call_down_mule": AbilityId.CALLDOWNMULE_CALLDOWNMULE.name,
    "call_down_supply": AbilityId.SUPPLYDROP_SUPPLYDROP.name,
    "salvage_bunker": AbilityId.EFFECT_SALVAGE.name,
    "dettach_barracks_from_techlab": CustomAbilities.BARRACKS_DETACH_TECHLAB.name,
    "dettach_barracks_from_reactor": CustomAbilities.BARRACKS_DETACH_REACTOR.name,
    "attach_barracks_to_free_techlab": CustomAbilities.BARRACKS_ATTACH_TECHLAB.name,
    "attach_barracks_to_free_reactor": CustomAbilities.BARRACKS_ATTACH_REACTOR.name,
    "dettach_factory_from_techlab": CustomAbilities.FACTORY_DETACH_TECHLAB.name,
    "dettach_factory_from_reactor": CustomAbilities.FACTORY_DETACH_REACTOR.name,
    "attach_factory_to_free_techlab": CustomAbilities.FACTORY_ATTACH_TECHLAB.name,
    "attach_factory_to_free_reactor": CustomAbilities.FACTORY_ATTACH_REACTOR.name,
    "dettach_starport_from_techlab": CustomAbilities.STARPORT_DETACH_TECHLAB.name,
    "dettach_starport_from_reactor": CustomAbilities.STARPORT_DETACH_REACTOR.name,
    "attach_starport_to_free_techlab": CustomAbilities.STARPORT_ATTACH_TECHLAB.name,
    "attach_starport_to_free_reactor": CustomAbilities.STARPORT_ATTACH_REACTOR.name,
}

TYPES = {
    "unit": OrderType.UNIT.name,
    "worker": OrderType.UNIT.name,
    "upgrade": OrderType.TECH.name,
    "structure": OrderType.STRUCTURE.name,
    "action": OrderType.ACTION.name,
}

EXCEPTION_IDS = {
    "OrbitalCommand": OrderType.TECH.name,
    "PlanetaryFortress": OrderType.TECH.name,
    "BarracksTechLab": OrderType.TECH.name,
    "BarracksReactor": OrderType.TECH.name,
    "FactoryTechLab": OrderType.TECH.name,
    "FactoryReactor": OrderType.TECH.name,
    "StarportTechLab": OrderType.TECH.name,
    "StarportReactor": OrderType.TECH.name,
    "worker_to_mins": OrderType.SCV_ACTION.name,
    "worker_to_gas": OrderType.SCV_ACTION.name,
    "3worker_to_gas": OrderType.SCV_ACTION.name,
    "worker_to_scout": OrderType.SCV_ACTION.name,
    "worker_from_scout": OrderType.SCV_ACTION.name,
}
