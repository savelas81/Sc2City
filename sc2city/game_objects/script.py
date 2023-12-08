from dataclasses import dataclass

from sc2.position import Point2

from utils import Status


@dataclass
class Script:
    id: str  # TODO: Create a list of scripts and connect this to the options
    target: Point2
    status: Status = Status.PENDING
    comment: str = ""

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)
