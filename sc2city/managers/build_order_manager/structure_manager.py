from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from Sc2City import Sc2City


# TODO: Add logic for controlling movable structures
class StructureManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot

    # TODO: Add logic for add-ons, researches and building upgrades (e.g. planetary fortress)
    def execute_builds(self) -> None:
        pass
