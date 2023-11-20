import math

class EnemyExpansions:

    def __init__(self, ai=None):
        self.ai = ai
        self.expansions: list = []
        self.natural = None
        self.third = None
        self.fourth = None
        self.fifth = None

    async def cache_enemy_expansions(self):
        expansions: list = self.ai.expansion_locations_list

        for t in range(0, 4):
            closest = None
            distance = math.inf
            for el in expansions:

                def is_near_to_expansion(t):
                    return t.distance_to(el) < self.ai.EXPANSION_GAP_THRESHOLD

                if any(map(is_near_to_expansion, self.ai.townhalls)):
                    # already taken
                    continue

                startp = self.ai.enemy_start_locations[0]
                d = await self.ai.client.query_pathing(startp, el)
                if d is None:
                    continue

                if d < distance:
                    distance = d
                    closest = el

            self.expansions.append(closest)
            expansions.remove(closest)
        print(self.ai.enemy_start_locations[0])
        print(self.expansions)
        self.natural = self.expansions[0]
        self.third = self.expansions[1]
        self.fourth = self.expansions[2]
        self.fifth = self.expansions[3]
