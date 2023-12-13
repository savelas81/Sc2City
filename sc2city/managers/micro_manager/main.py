import numpy as np
from typing import TYPE_CHECKING

from sc2.position import Point2, Point3

if TYPE_CHECKING:
    from Sc2City import Sc2City


# TODO: Implement army logic with scripts where the army distribution is decided here and the scripts are executed by the units manager
class MicroManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    def set_initial_unit_scripts(self) -> None:
        # TODO: Add logic to select initial script for units
        pass

    def update_unit_scripts(self) -> None:
        # TODO: Add logic to rearrange unit groups and select scripts based on game state
        pass
