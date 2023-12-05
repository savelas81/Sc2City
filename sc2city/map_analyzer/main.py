from sc2.bot_ai import BotAI


class MapAnalyzer:
    def __init__(self, bot: BotAI):
        self.bot = bot
        self.enemy_expansions = []

    async def cache_enemy_expansions(self):
        expansions = self.bot.expansion_locations_list
        enemy_start_location = self.bot.enemy_start_locations[0]
        distances = []

        for expansion in expansions:
            path_distance = await self.bot.client.query_pathing(
                enemy_start_location, expansion
            )
            if path_distance is not None:
                distances.append((path_distance, expansion))

        distances.sort(key=lambda x: x[0])
        self.enemy_expansions = [expansion for _, expansion in distances]
