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

# Loguru:
import loguru

# Math:
import math

# Constants:
TRANSITION_DISTANCE: float = 1.8
MINIMUM_DISTANCE: float = 0.4

SCV_RADIUS: float = 0.375

# Classes:
"""
* A utility class that contains methods for SCVManager to use.
*
* @param AI --> The SC2City AI object.
*
"""


class SCVManagerUtil:
    def __init__(self, AI: BotAI = None) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

    # Methods:
    """
    * A method to get all the possible mining positions.
    *
    * @param mineral_field --> The mineral field unit to pivot around.
    *
    * @returns A list of possible Point2 objects.
    """

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

    """
    * A method to have the specified SCV speed mine their specified mineral field.
    *
    * @param SCV --> The specified SCV unit object.
    *
    * @param target_mineral_field_tag --> The mineral field's tag.
    *
    * @param mineral_collector_dict --> A dictionary containing a mapping of the SCVs' mineral field.
    """

    def speed_mine_minerals_single(
        self,
        SCV: Unit,
        target_mineral_field_tag: int,
        mineral_collector_dict: typing.Dict[int, int],
    ) -> None:
        match SCV.is_carrying_resource:
            case True:
                if len(SCV.orders) < 2:
                    townhall: typing.Optional[
                        Unit
                    ] = self.AI.townhalls.ready.closest_to(SCV)
                    if townhall is None:
                        loguru.logger.info(
                            "Cannot locate a townhall for SCV of tag {} to return minerals to.".format(
                                SCV.tag
                            )
                        )
                        return None

                    if (
                        SCV.distance_to(townhall)
                        < TRANSITION_DISTANCE + townhall.radius + SCV_RADIUS
                    ):
                        if (
                            SCV.distance_to(townhall)
                            < MINIMUM_DISTANCE + townhall.radius + SCV_RADIUS
                        ):
                            SCV(AbilityId.SMART, townhall, queue=False)

                            return None

                        waypoint: Point2 = townhall.position.towards(
                            SCV, townhall.radius + SCV_RADIUS
                        )

                        SCV.move(waypoint)
                        SCV(AbilityId.SMART, townhall, queue=True)

                    return None

            case False:
                specified_mineral_field: typing.Optional[
                    Unit
                ] = self.AI.mineral_field.find_by_tag(tag=target_mineral_field_tag)

                if specified_mineral_field is None:
                    # await self.AI.SCVManager.remove_unit_tag_from_lists(SCV.tag)
                    loguru.logger.info(
                        "Cannot locate the mineral field with tag {}".format(
                            str(target_mineral_field_tag)
                        )
                    )
                    return None

                if SCV.is_idle:
                    SCV.gather(target=specified_mineral_field)
                    return None

                if len(SCV.orders) < 2:
                    if len(SCV.orders) == 1 and SCV.orders[0].target != target_mineral_field_tag:
                        if SCV.orders[0].target not in self.AI.mineral_field.tags:
                            loguru.logger.info("SCV with tag {} was targeting non mineral field.".format(str(SCV.tag)))
                            SCV.gather(specified_mineral_field)
                        else:
                            mineral_collector_dict[SCV.tag] = SCV.orders[0].target
                        return None

                    if (
                        MINIMUM_DISTANCE + specified_mineral_field.radius + SCV_RADIUS
                        < SCV.distance_to(specified_mineral_field)
                        < TRANSITION_DISTANCE + specified_mineral_field.radius + SCV_RADIUS
                    ):
                        mining_positions: typing.List[Point2] = self.get_mining_positions(
                            mineral_field=specified_mineral_field
                        )

                        minimum_distance: float = math.inf
                        closest: Point2 = Point2((0, 0))

                        for position in mining_positions:
                            if self.AI.in_pathing_grid(position) is False:
                                continue

                            distance: float = position.distance_to(SCV)
                            if distance < minimum_distance:
                                minimum_distance = distance
                                closest = position

                        if closest != Point2((0, 0)):
                            SCV.move(closest)
                            SCV(
                                AbilityId.SMART,
                                target=specified_mineral_field,
                                queue=True,
                            )
