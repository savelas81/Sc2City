import json
import heapq

from sc2.bot_ai import BotAI
from sc2.data import Race
from sc2.ids.unit_typeid import UnitTypeId

from config import MapType
from sc2city.utils import BuildTypes
from sc2city.game_objects import PositionPriority, MAP_PINS, PositionPriorityLists


class BuildingPlacementExtractor(BotAI):
    race = Race.Terran

    def __init__(
        self,
        main_bot_path: str,
        map_type=MapType.ONE_SIDE,
        build_type=BuildTypes.ONE_BASE,
    ):
        self.main_bot_path = main_bot_path
        self.map_type = map_type
        self.build_type = build_type
        self.map_pins_saved = False

    async def on_start(self):
        pass

    async def on_step(self, iteration):
        if (
            iteration == 0
            and self.map_type == MapType.ONE_SIDE
            and not any(
                structure.type_id == UnitTypeId.BARRACKS
                for structure in self.structures
            )
        ):
            print("Wrong starting position for one sided map. Leaving game.")
            await self.client.leave()  # This can't be called from on_start, since the game needs to start for this method to work

        if iteration != 30:  # Wait a few frames for supply depots to lower
            return

        player_map_pins = self.get_map_pins()
        self.save_map_pins(player_map_pins)

        if self.map_type == MapType.BOTH_SIDES:
            enemy_map_pins = self.get_map_pins(player=False)
            self.save_map_pins(enemy_map_pins)

        print("Map pins saved. Leaving game.")
        self.map_pins_saved = True
        await self.client.leave()

    def get_map_pins(self, player=True) -> PositionPriorityLists:
        positions_dict = {key: [] for key in PositionPriority}
        structures = self.structures if player else self.enemy_structures

        for structure in structures:
            if structure.type_id in MAP_PINS:
                priority, order = MAP_PINS[structure.type_id]
                positions_dict[priority].append((order, structure.position))

        for key in positions_dict:
            positions_dict[key] = [
                x[1]
                for x in heapq.nsmallest(len(positions_dict[key]), positions_dict[key])
            ]
        return positions_dict

    def save_map_pins(self, map_pins: PositionPriorityLists) -> None:
        path = self.build_type.value
        name = self.game_info.map_name + str(self.start_location) + ".json"
        filename = self.main_bot_path + "/" + path + name
        map_pins_str = {key.name: value for key, value in map_pins.items()}
        with open(filename, "w") as f:
            json.dump(map_pins_str, f, indent=2)
