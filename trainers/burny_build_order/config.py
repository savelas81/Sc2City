from dataclasses import dataclass

from sc2city.utils import OrderType


@dataclass
class BurnyOrder:
    id: int
    name: str
    type: str
    supply: int
    time: str
    frame: int


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
}
