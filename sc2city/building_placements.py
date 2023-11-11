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
        self.turret_positions_priority_1 = []
        self.turret_positions_priority_2 = []
        self.turret_positions_priority_3 = []
        self.macro_orbitals = []
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
            elif building.type_id == UnitTypeId.MISSILETURRET:
                self.turret_positions_priority_1.append(building.position)
            elif building.type_id == UnitTypeId.SPORECRAWLER:
                self.turret_positions_priority_2.append(building.position)
            elif building.type_id == UnitTypeId.PHOTONCANNON:
                self.turret_positions_priority_3.append(building.position)
            elif building.type_id == UnitTypeId.NEXUS:
                self.macro_orbitals.append(building.position)

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
        self.positions_dict["turret_positions_priority_1"] = self.turret_positions_priority_1
        self.positions_dict["turret_positions_priority_2"] = self.turret_positions_priority_2
        self.positions_dict["turret_positions_priority_3"] = self.turret_positions_priority_3
        self.positions_dict["macro_orbitals"] = self.macro_orbitals
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
                self.turret_positions_priority_1 = self.positions_dict["turret_positions_priority_1"]
                self.turret_positions_priority_2 = self.positions_dict["turret_positions_priority_2"]
                self.turret_positions_priority_3 = self.positions_dict["turret_positions_priority_3"]
                self.macro_orbitals = self.positions_dict["macro_orbitals"]


        except (OSError, IOError) as e:
            print("No chat data found.")
            print(e)

    def draw_debug(self):
        red = Point3((255, 0, 0))
        yellow = Point3((255, 255, 0))
        green = Point3((0, 255, 0))
        blue = Point3((0, 0, 255))
        white = Point3((255, 255, 255))
        draw_addon = False
        """barrack placement debugs below"""
        for p in self.building_positions_priority_1:
            pos = Point2(p)
            size = 1.45
            color = red
            draw_addon = True
            self.draw_debug_single(pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon)
        for p in self.building_positions_priority_2:
            pos = Point2(p)
            size = 1.45
            color = yellow
            draw_addon = True
            self.draw_debug_single(pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon)

        """engineeringbay etc placement debug """
        for p in self.auxiliary_buildings_1:
            pos = Point2(p)
            size = 1.45
            color = red
            draw_addon = False
            self.draw_debug_single(pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon)
            self.draw_debug_single(pos2=pos, size=(size - 0.05), height=0.3, color=color, draw_addon=draw_addon)

        """depot placement debug"""
        for p in self.supplydepot_positions_priority_1:
            pos = Point2(p)
            size = 0.95
            color = red
            draw_addon = False
            self.draw_debug_single(pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon)
        for p in self.supplydepot_positions_priority_2:
            pos = Point2(p)
            size = 0.95
            color = yellow
            draw_addon = False
            self.draw_debug_single(pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon)

        """turret placement debug"""
        for p in self.turret_positions_priority_1:
            pos = Point2(p)
            size = 0.95
            color = red
            draw_addon = False
            self.draw_debug_single(pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon)

        """macaro orbital placement debug"""
        for p in self.macro_orbitals:
            pos = Point2(p)
            size = 2.49
            color = red
            draw_addon = False
            self.draw_debug_single(pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon)

    def draw_debug_single(self,
                          pos2=Point2((0, 0)),
                          size=0.45,
                          height=0.3,
                          color=Point3((255, 255, 255)),
                          draw_addon=False):
        p2 = Point2(pos2)
        h2 = self.ai.get_terrain_z_height(p2)
        pos = Point3((p2.x, p2.y, h2))
        point0 = Point3((pos.x - size, pos.y - size, pos.z + height))
        point1 = Point3((pos.x + size, pos.y + size, pos.z))
        self.ai.client.debug_box_out(point0, point1, color=color)
        if draw_addon:
            pos = Point3((p2.x + 2.5, p2.y - 0.5, h2))
            point0 = Point3((pos.x - 0.95, pos.y - 0.95, pos.z + height))
            point1 = Point3((pos.x + 0.95, pos.y + 0.95, pos.z))
            self.ai.client.debug_box_out(point0, point1, color=color)
