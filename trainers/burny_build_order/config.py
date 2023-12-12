from dataclasses import dataclass

from sc2.ids.ability_id import AbilityId

from sc2city.utils import OrderType
from sc2city.game_objects import CustomOrders


@dataclass
class BurnyOrder:
    id: int
    name: str
    type: str
    supply: int
    time: str
    frame: int


BURNY_ACTIONS = {
    "worker_to_mins": CustomOrders.WORKER_TO_MINS.name,
    "worker_to_gas": CustomOrders.WORKER_TO_GAS.name,
    "3worker_to_gas": CustomOrders.WORKER_TO_GAS_3.name,
    "worker_to_scout": CustomOrders.WORKER_TO_SCOUT.name,
    "worker_from_scout": CustomOrders.WORKER_FROM_SCOUT.name,
    "do_nothing_1_sec": CustomOrders.DO_NOTHING_1_SEC.name,
    "do_nothing_5_sec": CustomOrders.DO_NOTHING_5_SEC.name,
    "call_down_mule": AbilityId.CALLDOWNMULE_CALLDOWNMULE.name,
    "call_down_supply": AbilityId.SUPPLYDROP_SUPPLYDROP.name,
    "salvage_bunker": AbilityId.EFFECT_SALVAGE.name,
    "dettach_barracks_from_techlab": CustomOrders.BARRACKS_DETACH_TECHLAB.name,
    "dettach_barracks_from_reactor": CustomOrders.BARRACKS_DETACH_REACTOR.name,
    "attach_barracks_to_free_techlab": CustomOrders.BARRACKS_ATTACH_TECHLAB.name,
    "attach_barracks_to_free_reactor": CustomOrders.BARRACKS_ATTACH_REACTOR.name,
    "dettach_factory_from_techlab": CustomOrders.FACTORY_DETACH_TECHLAB.name,
    "dettach_factory_from_reactor": CustomOrders.FACTORY_DETACH_REACTOR.name,
    "attach_factory_to_free_techlab": CustomOrders.FACTORY_ATTACH_TECHLAB.name,
    "attach_factory_to_free_reactor": CustomOrders.FACTORY_ATTACH_REACTOR.name,
    "dettach_starport_from_techlab": CustomOrders.STARPORT_DETACH_TECHLAB.name,
    "dettach_starport_from_reactor": CustomOrders.STARPORT_DETACH_REACTOR.name,
    "attach_starport_to_free_techlab": CustomOrders.STARPORT_ATTACH_TECHLAB.name,
    "attach_starport_to_free_reactor": CustomOrders.STARPORT_ATTACH_REACTOR.name,
}

TYPES = {
    "unit": OrderType.PRODUCTION.name,
    "worker": OrderType.PRODUCTION.name,
    "upgrade": OrderType.PRODUCTION.name,
    "structure": OrderType.STRUCTURE.name,
    "action": OrderType.ACTION.name,
}

EXCEPTION_IDS = {
    "OrbitalCommand": OrderType.PRODUCTION.name,
    "PlanetaryFortress": OrderType.PRODUCTION.name,
    "BarracksTechLab": OrderType.PRODUCTION.name,
    "BarracksReactor": OrderType.PRODUCTION.name,
    "FactoryTechLab": OrderType.PRODUCTION.name,
    "FactoryReactor": OrderType.PRODUCTION.name,
    "StarportTechLab": OrderType.PRODUCTION.name,
    "StarportReactor": OrderType.PRODUCTION.name,
    "worker_to_mins": OrderType.SCV_ACTION.name,
    "worker_to_gas": OrderType.SCV_ACTION.name,
    "3worker_to_gas": OrderType.SCV_ACTION.name,
    "worker_to_scout": OrderType.SCV_ACTION.name,
    "worker_from_scout": OrderType.SCV_ACTION.name,
}
