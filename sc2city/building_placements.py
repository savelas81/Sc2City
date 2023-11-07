import json
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units


class BuildingPlacementSolver:
    def __init__(self, ai=None):
        self.ai = ai
        self.building_positions_priority_1 = []
        self.building_positions_priority_2 = []
        self.building_positions_priority_3 = []
        self.building_positions_priority_4 = []
        self.building_positions_priority_5 = []
        self.auxiliary_buildings_1 = []
        self.auxiliary_buildings_2 = []
        self.auxiliary_buildings_3 = []
        self.supplydepot_positions_priority_1 = []
        self.supplydepot_positions_priority_2 = []
        self.supplydepot_positions_priority_3 = []
        self.supplydepot_positions_priority_4 = []
        self.supplydepot_positions_priority_5 = []
        self.positions_dict = {}
        self.map_name = ""
        self.start_location_save = Point2((0, 0))

    def save_placements(self, buildings: Units):
        building: Unit
        for building in buildings:
            if building.type_id == UnitTypeId.BARRACKS:
                self.building_positions_priority_1.append(building.position)
            elif building.type_id == UnitTypeId.FACTORY:
                self.building_positions_priority_2.append(building.position)
            elif building.type_id == UnitTypeId.STARPORT:
                self.building_positions_priority_3.append(building.position)
            elif building.type_id == UnitTypeId.GATEWAY:
                self.building_positions_priority_4.append(building.position)
            elif building.type_id == UnitTypeId.ROBOTICSFACILITY:
                self.building_positions_priority_5.append(building.position)
            elif building.type_id == UnitTypeId.ENGINEERINGBAY:
                self.auxiliary_buildings_1.append(building.position)
            elif building.type_id == UnitTypeId.ARMORY:
                self.auxiliary_buildings_2.append(building.position)
            elif building.type_id == UnitTypeId.GHOSTACADEMY:
                self.auxiliary_buildings_3.append(building.position)
            elif building.type_id == UnitTypeId.SUPPLYDEPOTLOWERED:
                self.supplydepot_positions_priority_1.append(building.position)
            elif building.type_id == UnitTypeId.SUPPLYDEPOT:
                self.supplydepot_positions_priority_2.append(building.position)
            elif building.type_id == UnitTypeId.PYLON:
                self.supplydepot_positions_priority_3.append(building.position)
            elif building.type_id == UnitTypeId.TECHLAB:
                self.supplydepot_positions_priority_4.append(building.position)
            elif building.type_id == UnitTypeId.DARKSHRINE:
                self.supplydepot_positions_priority_5.append(building.position)

        self.positions_dict["building_positions_priority_1"] = self.building_positions_priority_1
        self.positions_dict["building_positions_priority_2"] = self.building_positions_priority_2
        self.positions_dict["building_positions_priority_3"] = self.building_positions_priority_3
        self.positions_dict["building_positions_priority_4"] = self.building_positions_priority_4
        self.positions_dict["building_positions_priority_5"] = self.building_positions_priority_5
        self.positions_dict["auxiliary_buildings_1"] = self.auxiliary_buildings_1
        self.positions_dict["auxiliary_buildings_2"] = self.auxiliary_buildings_2
        self.positions_dict["auxiliary_buildings_3"] = self.auxiliary_buildings_3
        self.positions_dict["supplydepot_positions_priority_1"] = self.supplydepot_positions_priority_1
        self.positions_dict["supplydepot_positions_priority_2"] = self.supplydepot_positions_priority_2
        self.positions_dict["supplydepot_positions_priority_3"] = self.supplydepot_positions_priority_3
        self.positions_dict["supplydepot_positions_priority_4"] = self.supplydepot_positions_priority_4
        self.positions_dict["supplydepot_positions_priority_5"] = self.supplydepot_positions_priority_5
        # print(self.positions_dict)
        self.save_data()

    def save_data(self):
        map_name = self.ai.game_info.map_name
        cc_position = self.ai.structures(UnitTypeId.COMMANDCENTER).first.position
        map_id = 'data/' + str(map_name) + str(cc_position) + '.json'
        # map_id = 'data/test.json'
        print(map_id)
        try:
            with open(map_id, 'w') as file:
                json.dump(self.positions_dict, file, indent=2)
        except (OSError, IOError) as e:
            print(str(e))

    def load_data(self):
        map_name = self.ai.game_info.map_name
        cc_position = self.ai.structures(UnitTypeId.COMMANDCENTER).first.position
        map_id = 'data/' + str(map_name) + str(cc_position) + '.json'
        # map_id = 'data/test.json'
        try:
            with open(map_id, 'r') as file:
                self.positions_dict = json.load(file)
                self.building_positions_priority_1 = self.positions_dict["building_positions_priority_1"]
                self.building_positions_priority_2 = self.positions_dict["building_positions_priority_2"]
                self.building_positions_priority_3 = self.positions_dict["building_positions_priority_3"]
                self.building_positions_priority_4 = self.positions_dict["building_positions_priority_4"]
                self.building_positions_priority_5 = self.positions_dict["building_positions_priority_5"]
                self.auxiliary_buildings_1 = self.positions_dict["auxiliary_buildings_1"]
                self.auxiliary_buildings_2 = self.positions_dict["auxiliary_buildings_2"]
                self.auxiliary_buildings_3 = self.positions_dict["auxiliary_buildings_3"]
                self.supplydepot_positions_priority_1 = self.positions_dict["supplydepot_positions_priority_1"]
                self.supplydepot_positions_priority_2 = self.positions_dict["supplydepot_positions_priority_2"]
                self.supplydepot_positions_priority_3 = self.positions_dict["supplydepot_positions_priority_3"]
                self.supplydepot_positions_priority_4 = self.positions_dict["supplydepot_positions_priority_4"]
                self.supplydepot_positions_priority_5 = self.positions_dict["supplydepot_positions_priority_5"]
                print(self.building_positions_priority_1)
                print(self.building_positions_priority_2)
                print(self.building_positions_priority_3)
                print(self.building_positions_priority_4)
                print(self.building_positions_priority_5)
        except (OSError, IOError) as e:
            print("No chat data found.")
            print(e)

    def draw_debug(self):
        pass

