import numpy as np
from typing import TYPE_CHECKING

from sc2.position import Point2, Point3

if TYPE_CHECKING:
    from Sc2City import Sc2City


# TODO: Implement army logic with scripts where the army distribution is decided here and the scripts are executed by the units manager
class MicroManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        # TODO: Find a cleaner way to implement scouting logic merging the two types (location and points)
        self.pending_scouting_locations: list[Point2] = []

    def set_initial_unit_scripts(self) -> None:
        # TODO: Add logic to select initial script for units
        self.pending_scouting_locations.append(
            self.bot.map_analyzer.enemy_expansions[0]
        )

    def update_unit_scripts(self) -> None:
        # TODO: Add logic to rearrange unit groups and select scripts based on game state
        if self.pending_scouting_locations:
            self.__update_pending_scouting_locations()

        if self.bot.pending_scouting_points is not None:
            self.__update_pending_scouting_points()

        if (
            self.pending_scouting_locations is None
            and self.bot.pending_scouting_points is None
        ):
            self.__remove_scouts()

    def __update_pending_scouting_locations(self) -> None:
        # TODO: Implement scouting logic for script selection and merge with __update_pending_scouting_points
        for location in self.pending_scouting_locations:
            if self.bot.is_visible(location):
                self.pending_scouting_locations.remove(location)
                print("Location scouting completed")

    def __update_pending_scouting_points(self) -> None:
        # TODO: Add flexibility for adding any number of scouts and scouting targets
        if self.bot.pending_scouting_points.sum() == 0:
            self.bot.pending_scouting_points = None
            print("Scouting completed")
            return
        else:
            visibility = np.transpose(self.bot.state.visibility.data_numpy)
            condition_list = [visibility == 2, visibility != 2]
            choice_list = [0, 1]
            remove_scouted_points = np.select(condition_list, choice_list)
            self.bot.pending_scouting_points *= remove_scouted_points
        if self.bot.debug:
            for x in range(0, self.bot.pending_scouting_points.shape[0]):
                for y in range(0, self.bot.pending_scouting_points.shape[1]):
                    if self.bot.pending_scouting_points[x, y] == 1:
                        p = Point2((x, y))
                        h2 = self.bot.get_terrain_z_height(p)
                        pos = Point3((p.x, p.y, h2))
                        size = 0.45
                        p0 = Point3((pos.x - size, pos.y - size, pos.z + size))
                        p1 = Point3((pos.x + size, pos.y + size, pos.z - 0))
                        c = Point3((255, 0, 0))
                        self.bot.client.debug_box_out(p0, p1, color=c)

    def __remove_scouts(self) -> None:
        # TODO: Add logic that can handle more than one scout
        self.bot.scouts.clear()
