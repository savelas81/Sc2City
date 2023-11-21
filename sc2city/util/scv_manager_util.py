# Imports:

# StarCraft II:
# > Position:
from sc2.position import Point2

# > Bot AI:
from sc2.bot_ai import BotAI

# > Unit:
from sc2.unit import Unit

# > IDs:
from sc2.ids.ability_id import AbilityId

# Typing:
import typing

# Math:
import math

# Constants:
TRANSITION_DISTANCE: int = 1.8
MINIMUM_DISTANCE: float = 0.4

SCV_RADIUS: float = 0.375

# Utility:

"""
DOC HERE SAVELAS EVEN THOUGH IT IS OBVIOUS WHAT IT DOES!!!!

TODO: Savelas add the documentation u stingy little butthole
# TODO: Clean this up.... I WILL DO ITCHRONCIES WILL DO IT 
"""


# Class:
class SCVManagerUtil:
    def __init__(self, AI: BotAI = None) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

    # Methods:
    def get_mining_positions(self, mineral_field: Unit = None) -> typing.List[Point2]:
        # Variables:
        position: Point2 = Point2(mineral_field.position)

        # Main:
        return [
            Point2((position.x - 0.5, position.y - (0.5 + SCV_RADIUS))),
            Point2((position.x - 0.5, position.y + (0.5 + SCV_RADIUS))),
            Point2((position.x + 0.5, position.y - (0.5 + SCV_RADIUS))),
            Point2((position.x + 0.5, position.y + (0.5 + SCV_RADIUS))),
            Point2((position.x - (1 + SCV_RADIUS), position.y)),
            Point2((position.x - (1 + SCV_RADIUS), position.y - (0.5 + SCV_RADIUS))),
            Point2((position.x - (1 + SCV_RADIUS), position.y + (0.5 + SCV_RADIUS))),
            Point2((position.x + (1 + SCV_RADIUS), position.y)),
            Point2((position.x + (1 + SCV_RADIUS), position.y - (0.5 + SCV_RADIUS))),
            Point2((position.x + (1 + SCV_RADIUS), position.y + (0.5 + SCV_RADIUS))),
        ]

    def speed_mine_minerals_single(
            self,
            SCV: Unit,
            target_mineral_field_tag: int,
            mineral_collector_dict: typing.Dict[int, int],
    ) -> None:
        if SCV.is_carrying_resource:
            if len(SCV.orders) < 2:
                target = self.AI.townhalls.ready.closest_to(SCV)
                if (
                        SCV.distance_to(target)
                        < TRANSITION_DISTANCE + target.radius + SCV.radius
                ):
                    if (
                            SCV.distance_to(target)
                            < MINIMUM_DISTANCE + target.radius + SCV.radius
                    ):
                        SCV(AbilityId.SMART, target, queue=False)
                        return

                    waypoint = target.position.towards(SCV, target.radius + SCV.radius)
                    SCV.move(waypoint)
                    SCV(AbilityId.SMART, target, queue=True)
            return
        else:
            target: Unit = self.AI.mineral_field.find_by_tag(
                tag=target_mineral_field_tag
            )
            if SCV.is_idle and target:
                SCV.gather(target)
                return

            if len(SCV.orders) < 2:
                if target:
                    if len(SCV.orders) == 1 and SCV.orders[0].target != target.tag:
                        if SCV.orders[0].target not in self.AI.mineral_field.tags:
                            # TODO: Loguru print("scv_manager: scv has invalid target ID")
                            SCV.gather(target)
                        else:
                            mineral_collector_dict[SCV.tag] = SCV.orders[0].target
                        return
                    if (
                            MINIMUM_DISTANCE + target.radius + SCV.radius
                            < SCV.distance_to(target)
                            < TRANSITION_DISTANCE + target.radius + SCV.radius
                    ):
                        mining_positions = self.get_mining_positions(
                            mineral_field=target
                        )
                        closest = Point2((0, 0))
                        min_dist = math.inf
                        for pos in mining_positions:
                            if not self.AI.in_pathing_grid(pos):
                                continue
                            dist = pos.distance_to(SCV)
                            if dist < min_dist:
                                min_dist = dist
                                closest = pos
                        if closest != Point2((0, 0)):
                            waypoint = closest
                            SCV.move(waypoint)
                            SCV(AbilityId.SMART, target, queue=True)
                return
