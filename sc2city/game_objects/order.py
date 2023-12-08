from dataclasses import dataclass

from sc2.ids.unit_typeid import UnitTypeId

from utils import Status, OrderType


@dataclass
class Order:
    type: OrderType
    conditional: bool
    conditional_behavior: str  # TODO: Enumerate the possible values
    id: UnitTypeId
    target_value_behavior: bool = False
    target_value_or_quantity_value: int = 1
    status: Status = Status.PENDING
    comment: str = ""

    @classmethod
    def from_dict(cls, dct):
        dct["type"] = OrderType[dct["type"]]
        dct["id"] = UnitTypeId[dct["id"]]
        return cls(**dct)
