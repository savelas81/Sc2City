from dataclasses import dataclass

from sc2.ids.unit_typeid import UnitTypeId


@dataclass
class ScoutTime:
    id: UnitTypeId = UnitTypeId.SCV
    time: int = 37
    comment: str = ""

    @classmethod
    def from_dict(cls, dct):
        dct["id"] = UnitTypeId[dct["id"]]
        return cls(**dct)
