from dataclasses import dataclass


@dataclass
class Order:
    request_type: str  # TODO: Enumerate the possible values
    conditional: bool
    conditional_behavior: str  # TODO: Enumerate the possible values
    id: str  # TODO: Connect to the API's UnitTypeID options
    target_value_behavior: bool
    target_value_or_quantity_value: int
    comment: str

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)
