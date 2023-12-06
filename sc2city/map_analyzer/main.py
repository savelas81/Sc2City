from sc2.bot_ai import BotAI
from sc2.position import Point2


class MapAnalyzer:
    def __init__(self, bot: BotAI):
        self.bot = bot
        self.expansions = []
        self.enemy_expansions = []

    async def get_expansions(self) -> None:
        expansions = self.bot.expansion_locations_list
        starting_location = self.bot.start_location
        enemy_start_location = self.bot.enemy_start_locations[0]

        distances = await self.__calculate_path_distances(starting_location, expansions)
        enemy_distances = await self.__calculate_path_distances(
            enemy_start_location, expansions
        )

        self.expansions = [expansion for _, expansion in distances]
        self.enemy_expansions = [expansion for _, expansion in enemy_distances]

    def create_influence_maps(self):
        pass

    async def __calculate_path_distances(
        self, starting_position: Point2, goals: list[Point2]
    ) -> list[tuple[float, Point2]]:
        distances = []
        for goal in goals:
            path_distance = await self.bot.client.query_pathing(starting_position, goal)
            if path_distance is not None:
                distances.append((path_distance, goal))
        distances.sort(key=lambda x: x[0])
        return distances
