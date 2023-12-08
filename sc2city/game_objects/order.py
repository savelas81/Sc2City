from dataclasses import dataclass

from sc2.ids.unit_typeid import UnitTypeId

from utils import Status, OrderType


@dataclass
class Order:
    type: OrderType
    id: UnitTypeId
    priority: int = 0
    target_value: int = 1
    conditional: bool = True
    conditional_behavior: str = "skip"  # TODO: Enumerate the possible values
    target_value_behavior: bool = False
    status: Status = Status.PENDING
    comment: str = ""

    @classmethod
    def from_dict(cls, dct):
        dct["type"] = OrderType[dct["type"]]
        dct["id"] = UnitTypeId[dct["id"]]
        return cls(**dct)
