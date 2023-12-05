from sc2.bot_ai import BotAI


class EnemyExpansions:
    def __init__(self, bot: BotAI):
        self.bot = bot
        self.expansions: list = []
        self.natural = None
        self.third = None
        self.fourth = None
        self.fifth = None

    async def cache_enemy_expansions(self):
        all_expansions = self.bot.expansion_locations_list
        enemy_start_location = self.bot.enemy_start_locations[0]
        distances = []

        for expansion in all_expansions:
            path_distance = await self.bot.client.query_pathing(
                enemy_start_location, expansion
            )
            if path_distance is not None:
                distances.append((path_distance, expansion))

        distances.sort(key=lambda x: x[0])
        self.expansions = [expansion for _, expansion in distances]

        self.natural = self.expansions[0]
        self.third = self.expansions[1]
        self.fourth = self.expansions[2]
        self.fifth = self.expansions[3]
