from dataclasses import dataclass


@dataclass
class ScoutTime:
    id: str
    time: int
    comment: str

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)
