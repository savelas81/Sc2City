# Imports:

# StarCraft II:
# > Position:
from sc2.position import Point2, Point3

# > Units:
from sc2.units import Units

# > Unit:
from sc2.unit import Unit

# > IDs:
from sc2.ids.unit_typeid import UnitTypeId

# JSON:
import json

# Enum:
import enum


# Classes:
class MapType(enum.Enum):
    ONEBASE = enum.auto()
    STANDARD = enum.auto()
    PROXY = enum.auto()


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
        self.expansion_priority_1 = []
        self.expansion_priority_2 = []
        self.expansion_priority_3 = []
        self.macro_orbitals = []
        self.bunkers = []
        self.sensor_towers = []
        self.positions_dict = {}
        self.map_name = ""
        self.start_location_save = Point2((0, 0))

    async def get_placement_for(self, structure_type_id=UnitTypeId.BARRACKS):
        if structure_type_id in [UnitTypeId.SUPPLYDEPOT]:
            if self.ai.OpenerManager.manager_is_active:
                for position in self.ai.main_base_ramp.corner_depots:
                    if await self.this_valid_building_location(
                        structure_type_id=structure_type_id, position=position
                    ):
                        return position

            for position in [
                *self.supplydepot_positions_priority_1,
                *self.supplydepot_positions_priority_2,
                *self.supplydepot_positions_priority_3,
                *self.supplydepot_positions_priority_4,
                *self.supplydepot_positions_priority_5,
            ]:
                if await self.this_valid_building_location(
                    structure_type_id=structure_type_id, position=position
                ):
                    return position

        if structure_type_id in [
            UnitTypeId.BARRACKS,
            UnitTypeId.FACTORY,
            UnitTypeId.STARPORT,
        ]:
            for position in [
                *self.building_positions_priority_1,
                *self.building_positions_priority_2,
                *self.building_positions_priority_3,
                *self.building_positions_priority_4,
                *self.building_positions_priority_5,
            ]:
                if await self.this_valid_building_location(
                    structure_type_id=structure_type_id, position=position
                ):
                    return position

        if structure_type_id in [
            UnitTypeId.ENGINEERINGBAY,
            UnitTypeId.GHOSTACADEMY,
            UnitTypeId.ARMORY,
            UnitTypeId.FUSIONCORE,
        ]:
            for position in [
                *self.auxiliary_buildings_1,
                *self.auxiliary_buildings_2,
                *self.auxiliary_buildings_3,
            ]:
                if await self.this_valid_building_location(
                    structure_type_id=structure_type_id, position=position
                ):
                    return position

        if structure_type_id in [UnitTypeId.MISSILETURRET]:
            for position in [
                *self.turret_positions_priority_1,
                *self.turret_positions_priority_2,
                *self.turret_positions_priority_3,
            ]:
                if await self.this_valid_building_location(
                    structure_type_id=structure_type_id, position=position
                ):
                    return position

        if structure_type_id == UnitTypeId.COMMANDCENTER:
            for position in [
                *self.expansion_priority_1,
                *self.expansion_priority_2,
                *self.expansion_priority_3,
            ]:
                if await self.this_valid_building_location(
                    structure_type_id=structure_type_id, position=position
                ):
                    return position

        if (
            structure_type_id == UnitTypeId.ORBITALCOMMAND
        ):  # special case for macro orbitals
            for position in self.macro_orbitals:
                if await self.this_valid_building_location(
                    structure_type_id=structure_type_id, position=position
                ):
                    return position

        if structure_type_id == UnitTypeId.BUNKER:  # special case for macro orbitals
            for position in self.bunkers:
                if await self.this_valid_building_location(
                    structure_type_id=structure_type_id, position=position
                ):
                    return position

        if (
            structure_type_id == UnitTypeId.SENSORTOWER
        ):  # special case for macro orbitals
            for position in self.sensor_towers:
                if await self.this_valid_building_location(
                    structure_type_id=structure_type_id, position=position
                ):
                    return position

        print("Building_placements: No position for " + str(structure_type_id))
        return None

    async def this_valid_building_location(
        self, structure_type_id=UnitTypeId.BARRACKS, position=Point2((0, 0))
    ):
        # TODO this function should check also that this is safe location to build
        # TODO maybe even check enemy units in memory?
        need_addon = False
        position = Point2(position)
        if structure_type_id in [
            UnitTypeId.BARRACKS,
            UnitTypeId.FACTORY,
            UnitTypeId.STARPORT,
        ]:
            need_addon = True

        if await self.ai.can_place_single(structure_type_id, position):
            if not need_addon or await self.ai.can_place_single(
                UnitTypeId.SUPPLYDEPOT, position.offset(Point2((2.5, -0.5)))
            ):
                return True
        return False

    def save_placements(self, buildings: Units, map_type: MapType):
        building: Unit
        for building in buildings:
            match building.type_id:
                case UnitTypeId.BARRACKS:
                    self.building_positions_priority_1.append(building.position)
                case UnitTypeId.FACTORY:
                    self.building_positions_priority_2.append(building.position)
                case UnitTypeId.STARPORT:
                    self.building_positions_priority_3.append(building.position)
                case UnitTypeId.GATEWAY:
                    self.building_positions_priority_4.append(building.position)
                case UnitTypeId.ROBOTICSFACILITY:
                    self.building_positions_priority_5.append(building.position)
                case UnitTypeId.ENGINEERINGBAY:
                    self.auxiliary_buildings_1.append(building.position)
                case UnitTypeId.ARMORY:
                    self.auxiliary_buildings_2.append(building.position)
                case UnitTypeId.GHOSTACADEMY:
                    self.auxiliary_buildings_3.append(building.position)
                case UnitTypeId.SUPPLYDEPOTLOWERED:
                    self.supplydepot_positions_priority_1.append(building.position)
                case UnitTypeId.SUPPLYDEPOT:
                    self.supplydepot_positions_priority_2.append(building.position)
                case UnitTypeId.PYLON:
                    self.supplydepot_positions_priority_3.append(building.position)
                case UnitTypeId.TECHLAB:
                    self.supplydepot_positions_priority_4.append(building.position)
                case UnitTypeId.DARKSHRINE:
                    self.supplydepot_positions_priority_5.append(building.position)
                case UnitTypeId.MISSILETURRET:
                    self.turret_positions_priority_1.append(building.position)
                case UnitTypeId.SPORECRAWLER:
                    self.turret_positions_priority_2.append(building.position)
                case UnitTypeId.PHOTONCANNON:
                    self.turret_positions_priority_3.append(building.position)
                case UnitTypeId.ORBITALCOMMAND:
                    self.macro_orbitals.append(building.position)
                case UnitTypeId.NEXUS:
                    self.expansion_priority_1.append(building.position)
                case UnitTypeId.PLANETARYFORTRESS:
                    self.expansion_priority_2.append(building.position)
                case UnitTypeId.HATCHERY:
                    self.expansion_priority_3.append(building.position)
                case UnitTypeId.BUNKER:
                    self.bunkers.append(building.position)
                case UnitTypeId.SENSORTOWER:
                    self.sensor_towers.append(building.position)

        self.positions_dict[
            "building_positions_priority_1"
        ] = self.building_positions_priority_1
        self.positions_dict[
            "building_positions_priority_2"
        ] = self.building_positions_priority_2
        self.positions_dict[
            "building_positions_priority_3"
        ] = self.building_positions_priority_3
        self.positions_dict[
            "building_positions_priority_4"
        ] = self.building_positions_priority_4
        self.positions_dict[
            "building_positions_priority_5"
        ] = self.building_positions_priority_5
        self.positions_dict["auxiliary_buildings_1"] = self.auxiliary_buildings_1
        self.positions_dict["auxiliary_buildings_2"] = self.auxiliary_buildings_2
        self.positions_dict["auxiliary_buildings_3"] = self.auxiliary_buildings_3
        self.positions_dict[
            "supplydepot_positions_priority_1"
        ] = self.supplydepot_positions_priority_1
        self.positions_dict[
            "supplydepot_positions_priority_2"
        ] = self.supplydepot_positions_priority_2
        self.positions_dict[
            "supplydepot_positions_priority_3"
        ] = self.supplydepot_positions_priority_3
        self.positions_dict[
            "supplydepot_positions_priority_4"
        ] = self.supplydepot_positions_priority_4
        self.positions_dict[
            "supplydepot_positions_priority_5"
        ] = self.supplydepot_positions_priority_5
        self.positions_dict[
            "turret_positions_priority_1"
        ] = self.turret_positions_priority_1
        self.positions_dict[
            "turret_positions_priority_2"
        ] = self.turret_positions_priority_2
        self.positions_dict[
            "turret_positions_priority_3"
        ] = self.turret_positions_priority_3
        self.positions_dict["macro_orbitals"] = self.macro_orbitals
        self.positions_dict["expansion_priority_1"] = self.expansion_priority_1
        self.positions_dict["expansion_priority_2"] = self.expansion_priority_2
        self.positions_dict["expansion_priority_3"] = self.expansion_priority_3
        self.positions_dict["bunkers"] = self.bunkers
        self.positions_dict["sensor_towers"] = self.sensor_towers
        # print(self.positions_dict)
        self.save_data(map_type=map_type)

    def save_data(self, map_type: MapType):
        map_name = self.ai.game_info.map_name
        cc_position = self.ai.structures(UnitTypeId.COMMANDCENTER).first.position
        match map_type:
            case MapType.STANDARD:
                map_id = "data/standard/" + str(map_name) + str(cc_position) + ".json"
            case MapType.ONEBASE:
                map_id = "data/onebase/" + str(map_name) + str(cc_position) + ".json"
            case MapType.PROXY:
                map_id = "data/proxy/" + str(map_name) + str(cc_position) + ".json"
        # map_id = "data/" + str(map_name) + str(cc_position) + ".json"
        # map_id = 'data/test.json'
        try:
            with open(map_id, "w") as file:
                json.dump(self.positions_dict, file, indent=2)
                print(map_id)
        except (OSError, IOError) as e:
            print(str(e))

    def load_data(self, map_type: MapType):
        map_name = self.ai.game_info.map_name
        cc_position = self.ai.structures(UnitTypeId.COMMANDCENTER).first.position
        match map_type:
            case MapType.STANDARD:
                map_id = "data/standard/" + str(map_name) + str(cc_position) + ".json"
            case MapType.ONEBASE:
                map_id = "data/onebase/" + str(map_name) + str(cc_position) + ".json"
            case MapType.PROXY:
                map_id = "data/proxy/" + str(map_name) + str(cc_position) + ".json"
        # map_id = "data/" + str(map_name) + str(cc_position) + ".json"
        # map_id = 'data/test.json'
        try:
            with open(map_id, "r") as file:
                self.positions_dict = json.load(file)
                self.building_positions_priority_1 = self.positions_dict[
                    "building_positions_priority_1"
                ]
                self.building_positions_priority_2 = self.positions_dict[
                    "building_positions_priority_2"
                ]
                self.building_positions_priority_3 = self.positions_dict[
                    "building_positions_priority_3"
                ]
                self.building_positions_priority_4 = self.positions_dict[
                    "building_positions_priority_4"
                ]
                self.building_positions_priority_5 = self.positions_dict[
                    "building_positions_priority_5"
                ]
                self.auxiliary_buildings_1 = self.positions_dict[
                    "auxiliary_buildings_1"
                ]
                self.auxiliary_buildings_2 = self.positions_dict[
                    "auxiliary_buildings_2"
                ]
                self.auxiliary_buildings_3 = self.positions_dict[
                    "auxiliary_buildings_3"
                ]
                self.supplydepot_positions_priority_1 = self.positions_dict[
                    "supplydepot_positions_priority_1"
                ]
                self.supplydepot_positions_priority_2 = self.positions_dict[
                    "supplydepot_positions_priority_2"
                ]
                self.supplydepot_positions_priority_3 = self.positions_dict[
                    "supplydepot_positions_priority_3"
                ]
                self.supplydepot_positions_priority_4 = self.positions_dict[
                    "supplydepot_positions_priority_4"
                ]
                self.supplydepot_positions_priority_5 = self.positions_dict[
                    "supplydepot_positions_priority_5"
                ]
                self.turret_positions_priority_1 = self.positions_dict[
                    "turret_positions_priority_1"
                ]
                self.turret_positions_priority_2 = self.positions_dict[
                    "turret_positions_priority_2"
                ]
                self.turret_positions_priority_3 = self.positions_dict[
                    "turret_positions_priority_3"
                ]
                self.macro_orbitals = self.positions_dict["macro_orbitals"]
                self.expansion_priority_1 = self.positions_dict["expansion_priority_1"]
                self.expansion_priority_2 = self.positions_dict["expansion_priority_2"]
                self.expansion_priority_3 = self.positions_dict["expansion_priority_3"]
                self.bunkers = self.positions_dict["bunkers"]
                self.sensor_towers = self.positions_dict["sensor_towers"]

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
        """demo comment"""
        for p in self.building_positions_priority_1:
            pos = Point2(p)
            size = 1.45
            color = red
            draw_addon = True
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )
        for p in self.building_positions_priority_2:
            pos = Point2(p)
            size = 1.45
            color = yellow
            draw_addon = True
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )

        """engineeringbay etc placement debug """
        for p in self.auxiliary_buildings_1:
            pos = Point2(p)
            size = 1.45
            color = red
            draw_addon = False
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )
            self.draw_debug_single(
                pos2=pos,
                size=(size - 0.05),
                height=0.3,
                color=color,
                draw_addon=draw_addon,
            )

        """depot placement debug """
        for p in self.supplydepot_positions_priority_1:
            pos = Point2(p)
            size = 0.95
            color = red
            draw_addon = False
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )
        for p in self.supplydepot_positions_priority_2:
            pos = Point2(p)
            size = 0.95
            color = yellow
            draw_addon = False
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )

        """turret placement debug"""
        for p in self.turret_positions_priority_1:
            pos = Point2(p)
            size = 0.95
            color = red
            draw_addon = False
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )

        """macaro orbital placement debug"""
        for p in self.macro_orbitals:
            pos = Point2(p)
            size = 2.49
            color = white
            draw_addon = False
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )

        """expansion placement debug"""
        for p in self.expansion_priority_1:
            pos = Point2(p)
            size = 2.45
            color = red
            draw_addon = False
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )
        for p in self.expansion_priority_2:
            pos = Point2(p)
            size = 2.45
            color = yellow
            draw_addon = False
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )
        for p in self.expansion_priority_3:
            pos = Point2(p)
            size = 2.45
            color = green
            draw_addon = False
            self.draw_debug_single(
                pos2=pos, size=size, height=0.3, color=color, draw_addon=draw_addon
            )

    def draw_debug_single(
        self,
        pos2=Point2((0, 0)),
        size=0.45,
        height=0.3,
        color=Point3((255, 255, 255)),
        draw_addon=False,
    ):
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
