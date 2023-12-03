from sc2.unit import UnitTypeId
from managers import MapType

# Imports:
# > Bot AI:
from sc2.bot_ai import BotAI

# json
import json

# Typing:
import typing
import pprint

# Loguru:
import loguru


class BuildOrderManager:

    def __init__(self, AI: BotAI = None) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

        # Dictionaries:
        self.build_orders_file = {}

        # Lists:
        self.build_order = []

        # next build order item
        self.next_build_order = None

    async def on_the_start(self):
        self.load_data()
        pp = pprint.PrettyPrinter(indent=2)
        map_type = self.get_map_type()
        pp.pprint(map_type)
        self.build_order = self.get_build_order()
        pp.pprint(self.build_order)

    async def on_the_step(self):
        """
        gets next item from self.build_order and give that item to next part of code.
        """
        if len(self.build_order) <= 0:
            return
        if (await self.AI.UnitRequestFromJson.unit_queue_empty()
                and await self.AI.StructureQueueManager.structure_queue_empty()):
            if self.next_build_order is None and len(self.build_order) > 0:
                self.next_build_order = self.build_order.pop(0)
                print("build order list " + str(self.build_order))
                print("next build order" + str(self.next_build_order))
            if not eval(self.next_build_order.get("conditional")):
                if self.next_build_order.get("conditional_behaviour") == "skip":
                    self.next_build_order = None
                elif self.next_build_order.get("conditional_behaviour") == "wait":
                    return
                else:
                    behaviour = self.next_build_order.get("conditional_behaviour")
                    loguru.logger.info(
                        f"Build order had illegal conditional_behaviour: {str(behaviour)}"
                    )
            match self.next_build_order.get("request_type"):
                case "unit":
                    conditional = self.next_build_order.get("conditional")
                    ID = UnitTypeId[self.next_build_order.get("id")]
                    if self.next_build_order.get("target_value_behaviour") == "True":
                        target_value_behaviour = True
                    else:
                        target_value_behaviour = False
                    target_value_or_quantity_value = self.next_build_order.get("target_value_or_quantity_value")
                    await (self.AI.UnitRequestFromJson
                           .queue_unit(conditional=conditional,
                                       ID=ID,
                                       target_value_behaviour=target_value_behaviour,
                                       target_value_or_quantity_value=target_value_or_quantity_value)
                           )
                    self.next_build_order = None
                case "structure":
                    conditional = self.next_build_order.get("conditional")
                    ID = UnitTypeId[self.next_build_order.get("id")]
                    if self.next_build_order.get("target_value_behaviour") == "True":
                        target_value_behaviour = True
                    else:
                        target_value_behaviour = False
                    target_value_or_quantity_value = self.next_build_order.get("target_value_or_quantity_value")
                    await (self.AI.StructureQueueManager
                           .queue_building(conditional=conditional,
                                           ID=ID,
                                           target_value_behaviour=target_value_behaviour,
                                           target_value_or_quantity_value=target_value_or_quantity_value))
                    self.next_build_order = None

        """
        Execute build order for units.
        This is run every frame even if there is nothing to train
        """

    def save_data(self):
        try:
            with open('data/test.json', 'w') as file:
                json.dump(self.build_orders_file, file, indent=2)
        except (OSError, IOError) as e:
            print(str(e))

    def load_data(self):
        try:
            with open('data/test.json', 'r') as file:
                self.build_orders_file = json.load(file)
        except (OSError, IOError) as e:
            print("No build order data found.")
            print(e)

    def get_map_type(self) -> typing.Optional[MapType]:
        map_type: MapType = None
        if not self.build_orders_file.get("build_type"):
            loguru.logger.info(
                f"Not able to find build_type"
            )
            return None
        match self.build_orders_file.get("build_type"):
            case "ONEBASE":
                return MapType.ONEBASE
            case "PROXY":
                return MapType.PROXY
            case "STANDARD":
                return MapType.STANDARD
        loguru.logger.info(
            f"Wrong build_type in .json file"
        )

    def get_build_order(self) -> typing.Optional[list]:
        if not self.build_orders_file.get("build_order"):
            loguru.logger.info(
                f"Not able to find build_order"
            )
            return None
        return self.build_orders_file.get("build_order")

