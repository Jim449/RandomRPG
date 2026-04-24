from blueprint import Blueprint
from maze import Maze, IllegalMazeError
from area import Area
from location import Location, KeyObject
from encounter import Encounter
from conversation import Conversation
from unit import Presence
from storage import Storage

class MapBuilder:
    GREAT_MOUNTAINS: int = 0
    HIGHLANDS: int = 1
    COASTLINE: int = 2
    FOREST: int = 3
    DEEP_FOREST: int = 4
    RIVER: int = 5
    MEADOWS: int = 6
    HILLS: int = 7
    LAKESIDE: int = 8

    def __init__(self, storage: Storage):
        self.maze: Maze = None
        self.underground: Maze = None
        self.storage: Storage = storage
    
    def build(self):
        self.define_main_map()
        self.define_great_mountains()
        self.define_highlands()
        self.define_coastline()
        self.define_forest()
        self.define_deep_forest()
        self.define_river()
        self.define_meadows()
        self.define_hills()
        self.define_lakeside()
        self.maze.build_locations()
        self.define_underground_map()
        self.dig_great_mountains()
        self.dig_highlands()
        self.dig_coastline()
        self.dig_forest()
        self.dig_deep_forest()
        self.dig_river()
        self.dig_meadows()
        self.dig_hills()
        self.dig_lakeside()
        self.underground.build_locations()
    
    def define_main_map(self):
        """Defines the main map areas terrain and encounters.
        Generates a random room layout"""
        blueprint = Blueprint.main_map_blueprint()
        print(blueprint.get_layout())
        
        # This should get a lot of mountain terrain
        # Note, there are 13x13=169 internal cells
        # so I can't add too many obstacles
        area_0 = Area(0, "Great mountains",
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.FOREST, Location.MOUNTAIN),
                      pool_terrain_amount=(0, 3),
                      pool_terrain_growth=(0, 25),
                      line_terrain_amount=(0, 0),
                      large_obstacle_growth=(15, 20),
                      obstacle_coverage=(0.1, 0.2),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=12,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
        # Should get a lot of mountain terrain
        # but less than the great mountains
        # Gets some lakes
        area_1 = Area(1, "Highlands",
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.FOREST, Location.WATER, Location.MOUNTAIN),
                      pool_terrain_amount=(0, 3),
                      pool_terrain_growth=(0, 20),
                      line_terrain_amount=(0, 0),
                      large_obstacle_growth=(10, 15),
                      obstacle_coverage=(0.1, 0.2),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=6,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
        # Should get mostly lake areas with some mountains around them
        area_2 = Area(2, "Coastline",
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.FOREST),
                      pool_terrain_amount=(0, 1),
                      pool_terrain_growth=(0, 15),
                      line_terrain_amount=(0, 0),
                      large_obstacle_growth=(5, 10),
                      obstacle_coverage=(0.1, 0.2),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=2,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=6)
        
        # Should get a lot of forest terrain
        # as well as a few ponds and some fences
        area_3 = Area(3, "Forest",
                      base_tile=Location.PALE_GRASS,
                      allowed_obstacles=(Location.FOREST, Location.FENCE, Location.WATER),
                      pool_terrain_amount=(-1, 2),
                      pool_terrain_growth=(0, 10),
                      line_terrain_amount=(-1, 3),
                      large_obstacle_growth=(0, 0),
                      obstacle_coverage=(0.3, 0.4),
                      large_obstacles=tuple(),
                      large_obstacle_amount=0,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
        # Forest enemies aren't too strong
        area_3.add_encounter(Encounter(["Red_spider", "Red_spider"], [1, 1], encounter_weight=1))
        area_3.add_encounter(Encounter(["Red_spider", "Red_spider", "Red_spider"], [1, 1, 1], encounter_weight=1))
        area_3.add_encounter(Encounter(["Goblin"], [1], encounter_weight=1))
        area_3.add_encounter(Encounter(["Goblin", "Goblin"], [1, 1], encounter_weight=1))
        area_3.add_encounter(Encounter(["Gray_wolf"], [1], encounter_weight=1))

        # Should get the densest forest terrain
        # Not much variation, except for a large lake somewhere
        area_4 = Area(4, "Deep forest",
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.FOREST, Location.WATER),
                      pool_terrain_amount=(0, 0),
                      pool_terrain_growth=(10, 20),
                      line_terrain_amount=(0, 0),
                      large_obstacle_growth=(15, 20),
                      obstacle_coverage=(0.4, 0.5),
                      large_obstacles=(Location.WATER,),
                      large_obstacle_amount=1,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
        # Deep forest enemies are weak but numerous
        # A high defense stat will be useful here
        area_4.add_encounter(Encounter(["Red_spider", "Red_spider", "Red_spider"], [1, 1, 1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Red_spider", "Red_spider", "Red_spider", "Red_spider"], [1, 1, 1, 1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Black_bat"], [1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Black_bat", "Black_bat"], [1, 1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Goblin", "Goblin"], [1, 1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Gray_wolf", "Gray_wolf"], [1, 1], encounter_weight=1))

        # Should get a lot of water and some lake areas
        # Water shouldn't expand much
        # Forest terrain is dense and there may be some fences
        area_5 = Area(5, "River",
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.FENCE, Location.FOREST, Location.WATER),
                      pool_terrain_amount=(0, 0),
                      pool_terrain_growth=(5, 10),
                      line_terrain_amount=(-1, 3),
                      large_obstacle_growth=(0, 5),
                      obstacle_coverage=(0.2, 0.3),
                      large_obstacles=(Location.WATER,),
                      large_obstacle_amount=6,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=2)
        
        # Should get sparse forest terrain
        # as well as some ponds and fences
        area_6 = Area(6, "Meadows",
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.WATER, Location.FOREST, Location.FENCE, Location.OAK),
                      pool_terrain_amount=(-1, 2),
                      pool_terrain_growth=(0, 10),
                      line_terrain_amount=(-1, 3),
                      object_terrain_amount=(0, 2),
                      large_obstacle_growth=(0, 0),
                      obstacle_coverage=(0.1, 0.2),
                      large_obstacles=tuple(),
                      large_obstacle_amount=0,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
        # The encounters in the meadows are quite weak
        area_6.add_encounter(Encounter(["Red_spider"], [1], encounter_weight=2))
        area_6.add_encounter(Encounter(["Red_spider", "Red_spider"], [1, 1], encounter_weight=2))
        area_6.add_encounter(Encounter(["Goblin"], [1], encounter_weight=2, reward=5))
        
        conversation = Conversation([])
        conversation.add_quest("The wolf", 2, progress_quest=True)
        area_6.add_encounter(Encounter(["Gray_wolf"], [1],
                                       encounter_weight=1, 
                                       conversation=conversation))
        
        # Should get a lot of mountain terrain,
        # focusing on internal mountains over edge mountains
        # Vegetation is sparse
        area_7 = Area(7, "Hills",
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.FOREST),
                      pool_terrain_amount=(1, 3),
                      pool_terrain_growth=(0, 20),
                      line_terrain_amount=(0, 0),
                      large_obstacle_growth=(0, 5),
                      obstacle_coverage=(0.1, 0.2),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=3,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
        # For the hills, the enemies can be strong but not numerous
        # A high strength stat will be useful here
        area_7.add_encounter(Encounter(["Gray_wolf"], [1], encounter_weight=1))
        area_7.add_encounter(Encounter(["Orc"], [1], encounter_weight=2))
        area_7.add_encounter(Encounter(["Goblin"], [1], encounter_weight=1))
        area_7.add_encounter(Encounter(["Goblin", "Goblin"], [1, 1], encounter_weight=1))

        # Should get multiple lakes surrounded by mountains
        # Land areas will get less water and more mountains
        area_8 = Area(8, "Lakeside",
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.FOREST),
                      pool_terrain_amount=(0, 3),
                      pool_terrain_growth=(0, 25),
                      line_terrain_amount=(0, 0),
                      large_obstacle_growth=(5, 10),
                      obstacle_coverage=(0.2, 0.3),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=4,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=4)
        
        maze = Maze(3, 3, "overworld")
        for area in (area_0, area_1, area_2, area_3, area_4, area_5, area_6, area_7, area_8):
            maze.add_area(area)

        maze.build_maze(blueprint)
        self.maze = maze.copy()
        
        for tries in range(10):
            try:
                # Connects the maze areas
                self.maze.construct_connections()
                # Can give more randomness to maze area shapes
                # self.maze.exchange_rooms()
                self.maze.start_trails()
                # Creates rooms within the areas
                self.maze.construct_areas(add_intersections=1)
                break
            except IllegalMazeError as e:
                print(f"Attempt {tries} failed: {e}")
                self.maze = maze.copy()
        
        print(self.maze.get_layout())

        self.maze.place_large_obstacles()
        self.maze.place_inaccessible_tiles()
        self.maze.setup_locations()
        self.maze.clear_room_numbers()

    def define_great_mountains(self):
        # Assign id numbers to all rooms
        # Then I can manipulate the rooms to my liking
        great_mountains = self.maze.areas[0]
        # Rooms bordering to different areas get specific id numbers
        great_mountains.get_connecting_room(MapBuilder.HIGHLANDS).number = 72
        # Then I'll assign the remaining id numbers at random
        great_mountains.assign_room_numbers(73)

        # From here I can create presences
        # These are the NPC:s, item locations, cave entrances, events triggers, etc.
        # Then I should give conversations to these presences
        # These are the quests, messages, items, warps, etc.
        # Then I should create key objects
        # These override parts of the terrain and allows me to place my presences on the map
    
    def define_highlands(self):
        highlands = self.maze.areas[1]
        highlands.get_connecting_room(MapBuilder.DEEP_FOREST).number = 63
        highlands.get_connecting_room(MapBuilder.GREAT_MOUNTAINS).number = 64
        highlands.assign_room_numbers(65)

    def define_coastline(self):
        coastline = self.maze.areas[2]
        coastline.get_connecting_room(MapBuilder.RIVER).number = 54
        coastline.assign_room_numbers(55)

    def define_forest(self):
        forest = self.maze.areas[3]
        forest.get_connecting_room(MapBuilder.MEADOWS).number = 9
        forest.get_connecting_room(MapBuilder.DEEP_FOREST).number = 10
        forest.assign_room_numbers(11)

        # Witch house in the forest
        # Hands out a quest and sells spells
        witches_room = self.maze.get_room_of_number(11)
        witches_room.location.min_obstacle_coverage = 0.5
        witches_room.location.max_obstacle_coverage = 0.5
        witches_room.location.line_terrain_amount = (0, 0)
        witches_room.location.pool_terrain_amount = (1, 1)

        witch = Presence(sprite_path="resources/people/Commoner_female.png")
        witch.add_conversation(self.storage.get_conversation("the_witch"))
        witch.add_conversation(self.storage.get_conversation("the_witches_house", 0))
        witch.add_conversation(self.storage.get_conversation("the_witches_house", 2))
        witch.add_conversation(self.storage.get_conversation("the_witches_house", 3))

        witches_house = KeyObject(length=3, height=3, terrain=Location.HOUSE_3x2,
                                  presence=witch, presence_x=1, presence_y=2,
                                  entrance_type=Location.IMPORTANT_BLOCKING,
                                  entrance_x=1, entrance_y=2)
        witches_room.location.add_key_object(witches_house)

        # Goblin cave
        # Visit to clear a quest
        goblin_room = self.maze.get_room_of_number(12)
        goblin_room.location.allowed_obstacles = (Location.FOREST, Location.MOUNTAIN, Location.OAK)
        goblin_cave_terrain = [
            [30, 30, 30],
            [30, 30, 30],
            [30, 6, 30],
            [1, -1, 1]
        ]
        cave_warp = Presence(trigger_on_contact=True)
        cave_warp.add_warp("underground", 4, 0, 1)

        goblin_cave = KeyObject(length=3, height=4,
                                presence=cave_warp, presence_x=1, presence_y=2,
                                override_terrain=goblin_cave_terrain)
        goblin_room.location.add_key_object(goblin_cave)

    def define_deep_forest(self):
        deep_forest = self.maze.areas[4]
        deep_forest.get_connecting_room(MapBuilder.FOREST).number = 27
        deep_forest.get_connecting_room(MapBuilder.HILLS).number = 28
        deep_forest.get_connecting_room(MapBuilder.RIVER).number = 29
        deep_forest.get_connecting_room(MapBuilder.HIGHLANDS).number = 30
        deep_forest.assign_room_numbers(31)

    def define_river(self):
        river = self.maze.areas[5]
        river.get_connecting_room(MapBuilder.DEEP_FOREST).number = 36
        river.get_connecting_room(MapBuilder.LAKESIDE).number = 37
        river.get_connecting_room(MapBuilder.COASTLINE).number = 38
        river.assign_room_numbers(39)

    def define_meadows(self):
        meadows = self.maze.areas[6]
        meadows.get_connecting_room(MapBuilder.FOREST).number = 0
        meadows.get_connecting_room(MapBuilder.HILLS).number = 1
        meadows.assign_room_numbers(2)

        # Starting room, a safe zone with healing NPCs
        village_room = self.maze.get_room_of_number(2)
        village_room.location.safe_zone = True
        village_room.line_terrain_amount = (3, 3)
        village_room.pool_terrain_amount = (0, 0)

        # Isabel
        # She'll have to do without a name variable
        innkeeper = Presence(sprite_path="resources/people/Commoner_female.png",
                             conversation_names=[("the_innkeeper", 0),
                                                 ("the_wolf", 3)])
        inn = KeyObject(length=3, height=3, terrain=Location.HOUSE_3x2,
                        presence=innkeeper, presence_x=1, presence_y=2,
                        entrance_type=Location.IMPORTANT_BLOCKING,
                        entrance_x=1, entrance_y=2)
        village_room.location.add_key_object(inn)

        # Henry
        blacksmith = Presence(sprite_path="resources/people/Commoner_male.png",
                              conversation_names=[("the_blacksmith", 0),
                                                  ("the_hunters_cabin", 0),
                                                  ("the_hunters_cabin", 1),
                                                  ("the_blacksmith_shop", 0),
                                                  ("the_blacksmith_shop", 1)])
        
        smithy = KeyObject(length=3, height=3, terrain=Location.HOUSE_3x2,
                           presence=blacksmith, presence_x=1, presence_y=2,
                           entrance_type=Location.IMPORTANT_BLOCKING,
                           entrance_x=1, entrance_y=2)
        village_room.location.add_key_object(smithy)

        # Eliza
        # Needs a different sprite
        herbalist = Presence(sprite_path="resources/people/Commoner_female.png",
                             conversation_names=[("the_herbalist", 0),
                                                 ("the_herbalists_gift", 0),
                                                 ("the_druids_blade", 1)])
        
        apothecary = KeyObject(length=3, height=3, terrain=Location.HOUSE_3x2,
                               presence=herbalist, presence_x=1, presence_y=2,
                               entrance_type=Location.IMPORTANT_BLOCKING,
                               entrance_x=1, entrance_y=2)
        village_room.location.add_key_object(apothecary)

        # Hunters cabin. Hands out quests
        hunter_room = self.maze.get_room_of_number(3)
        hunter_room.location.line_terrain_amount = (0, 0)
        hunter_room.location.pool_terrain_amount = (1, 1)
        
        # Richard
        hunter = Presence(sprite_path="resources/people/Commoner_male.png",
                          conversation_names=[("the_hunter", 0),
                                              ("the_hunters_cabin", 2),
                                              ("the_wolf", 0),
                                              ("the_wolf", 1),
                                              ("the_wolf", 2)])

        # A small house surrounded by fences
        hunter_cabin_terrain = [
            [4, 11, 9, 9, 4],
            [4, 9, 9, 9, 4],
            [4, 0, 5, 0, 4],
            [4, 0, 0, 0, 4],
            [3, 3, -1, 3, 3],
        ]
        hunter_cabin = KeyObject(length=5, height=5,
                                 presence=hunter, presence_x=2, presence_y=2,
                                 override_terrain=hunter_cabin_terrain)
        hunter_room.location.add_key_object(hunter_cabin)

        # A great oak tree in the middle of a field
        # The player can pick up a hidden item
        great_oak_room = self.maze.get_room_of_number(4)
        great_oak_room.location.line_terrain_amount = (0, 0)
        great_oak_room.location.pool_terrain_amount = (0, 0)
        great_oak_room.location.object_terrain_amount = (0, 0)
        crescent_knife = Presence(conversation_names=[("the_druids_blade", 0)])
        oak_terrain = [
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, 10, 9, -1, -1, -1, -1],
            [-1, -1, -1, -1, 9, 9, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        ]
        the_oak = KeyObject(length=10, height=10,
                            presence=crescent_knife, presence_x=4, presence_y=4,
                            override_terrain=oak_terrain)
        great_oak_room.location.add_key_object(the_oak)

        # Some trees arranged in a pattern
        # I may want to add some fruit trees
        # with collectible healing items
        orchard = self.maze.get_room_of_number(5)
        orchard.location.pool_terrain_amount = (0, 0)
        orchard_terrain = [
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, 1, 1, -1, 1, 1, -1, 1, 1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, 1, 1, -1, 1, 1, -1, 1, 1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, 1, 1, -1, 1, 1, -1, 1, 1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, 1, 1, -1, 1, 1, -1, 1, 1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        ]
        the_orchard = KeyObject(length=10, height=9, x=1, y=1,
                                override_terrain=orchard_terrain)
        orchard.location.add_key_object(the_orchard)

        # A spider cave
        # Should be blocked by a web
        # The player will need to use a fire spell to reach the cave
        spider_room = self.maze.get_room_of_number(6)
        spider_cave_terrain = [
            [30, 30, 30],
            [30, 30, 30],
            [30, 6, 30],
            [-1, -1, -1]
        ]
        cave_warp = Presence(trigger_on_contact=True)
        cave_warp.add_warp("underground", 0, 0, 1)
        spider_cave = KeyObject(length=3, height=4,
                                presence=cave_warp, presence_x=1, presence_y=2,
                                override_terrain=spider_cave_terrain)
        spider_room.location.add_key_object(spider_cave)

        # Makes the forest entrance more apparent by adding a fence
        # The forest should be denser north of the fence
        # Consider adding a guard
        forest_entrance = self.maze.get_room_of_number(0)
        forest_entrance.location.allowed_obstacles = (Location.FOREST,)
        # forest_entrance.location.obstacle_coverage = (0.5, 0.6)
        fence_terrain = [
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
            [3, 3, 3, 3, 3, 3, -1, 3, 3, 3, 3, 3, 3]
        ]
        fence = KeyObject(length=13, height=5, x=1, y=1,
                          override_terrain=fence_terrain)
        forest_entrance.location.add_key_object(fence)

        # Indicate hill entrance by adding two hills
        # Consider adding a guard
        hills_entrance = self.maze.get_room_of_number(1)
        hills_terrain = [
            [30, 30, 30],
            [30, 30, 30],
            [30, 30, 30],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [30, 30, 30],
            [30, 30, 30],
            [30, 30, 30]
        ]
        twin_hills = KeyObject(length=3, height=9, x=11, y=3,
                               override_terrain=hills_terrain)
        hills_entrance.location.add_key_object(twin_hills)
    
    def define_hills(self):
        hills = self.maze.areas[7]
        hills.get_connecting_room(MapBuilder.MEADOWS).number = 18
        hills.get_connecting_room(MapBuilder.DEEP_FOREST).number = 19
        hills.get_connecting_room(MapBuilder.LAKESIDE).number = 20
        hills.assign_room_numbers(21)
    
    def define_lakeside(self):
        lakeside = self.maze.areas[8]
        lakeside.get_connecting_room(MapBuilder.HILLS).number = 45
        lakeside.get_connecting_room(MapBuilder.RIVER).number = 46
        lakeside.assign_room_numbers(47)
    
    def define_underground_map(self):
        """Creates an underground maze for all areas.
        These are small 2x2 areas where one might find npcs or clear some quests.
        Dungeons are not defined here."""
        underground_blueprint = Blueprint.underground_blueprint()
        
        area_0 = Area(0, "Great mountains", base_tile=Location.BRIGHT_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
        pool_terrain_amount=(0, 4), pool_terrain_growth=(0, 4))
        
        area_1 = Area(1, "Highlands", base_tile=Location.BRIGHT_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
        pool_terrain_amount=(0, 4), pool_terrain_growth=(0, 4))
        
        area_2 = Area(2, "Coastline", base_tile=Location.BRIGHT_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
        pool_terrain_amount=(0, 4), pool_terrain_growth=(0, 4))
        
        area_3 = Area(3, "Forest", base_tile=Location.PALE_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.PURPLE_WATER, Location.MUSHROOMS),
        obstacle_coverage=(0.1, 0.2),
        pool_terrain_amount=(3, 4), pool_terrain_growth=(0, 4))
        # Spiders and goblins in the forest underground
        area_3.add_encounter(Encounter(["Red_spider", "Red_spider", "Red_spider"], [1, 1, 1], encounter_weight=1))
        area_3.add_encounter(Encounter(["Goblin", "Goblin"], [1, 1], encounter_weight=1))
        
        area_4 = Area(4, "Deep forest", base_tile=Location.BRIGHT_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
        pool_terrain_amount=(0, 4), pool_terrain_growth=(0, 4))
        # Mostly bats down here
        area_4.add_encounter(Encounter(["Red_spider", "Red_spider", "Red_spider", "Red_spider"], [1, 1, 1, 1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Black_bat"], [1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Black_bat", "Black_bat"], [1, 1], encounter_weight=1))

        area_5 = Area(5, "River", base_tile=Location.BRIGHT_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
        pool_terrain_amount=(0, 4), pool_terrain_growth=(0, 4))
        
        area_6 = Area(6, "Meadows", base_tile=Location.BRIGHT_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
        pool_terrain_amount=(0, 4), pool_terrain_growth=(0, 4))
        # Only spiders in the meadows underground
        area_6.add_encounter(Encounter(["Red_spider", "Red_spider"], [1, 1], encounter_weight=1))

        area_7 = Area(7, "Hills", base_tile=Location.BRIGHT_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
        pool_terrain_amount=(0, 4), pool_terrain_growth=(0, 4))
        
        area_8 = Area(8, "Lakeside", base_tile=Location.BRIGHT_GREEN_ROCK,
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
        pool_terrain_amount=(0, 4), pool_terrain_growth=(0, 4))

        self.underground = Maze(3, 2, "underground")
        for area in (area_0, area_1, area_2, area_3, area_4, area_5, area_6, area_7, area_8):
            self.underground.add_area(area)

        self.underground.build_maze(underground_blueprint)
        print(self.underground.get_layout())

        for room in self.underground.rooms:
            for direction in range(4):
                room.set_terrain(direction, Location.MOUNTAIN)

        self.underground.place_large_obstacles()
        self.underground.place_inaccessible_tiles()
        self.underground.setup_locations()
        self.underground.clear_room_numbers()
    
    def dig_great_mountains(self):
        great_mountains = self.underground.areas[0]
        great_mountains.assign_room_numbers(32)
    
    def dig_highlands(self):
        highlands = self.underground.areas[1]
        highlands.assign_room_numbers(28)
    
    def dig_coastline(self):
        coastline = self.underground.areas[2]
        coastline.assign_room_numbers(24)
    
    def dig_forest(self):
        forest = self.underground.areas[3]
        forest.assign_room_numbers(4)

        goblin_room = self.underground.get_room_of_number(4)
        shaman_terrain = [
            [-2, -2, -2],
            [-2, -1, -2],
            [-2, -2, -2]
        ]
        goblin_encounter = Encounter(["Goblin_shaman", "Goblin"], [1, 1],
                                     block_escape=True)
        goblin_shaman = Presence(sprite_path="resources/people/Goblin_shaman_SMALL.png",
                                 encounter=goblin_encounter,
                                 conversation_names=[("the_witches_house", 1)])
        shaman_object = KeyObject(3, 3,
                                  presence=goblin_shaman, presence_x = 1, presence_y = 1,
                                  override_terrain = shaman_terrain)
        goblin_cave_terrain = [
            [-2, -1, -2],
            [30, 7, 30],
            [30, 30, 30],
            [30, 30, 30]
        ]
        cave_warp = Presence(trigger_on_contact=True)
        cave_warp.add_warp("overworld", 12, 0, -1)

        goblin_cave = KeyObject(length=3, height=4,
                                presence=cave_warp, presence_x=1, presence_y=1,
                                override_terrain=goblin_cave_terrain)
        goblin_room.location.add_key_object(goblin_cave)
        goblin_room.location.add_key_object(shaman_object)
    
    def dig_deep_forest(self):
        deep_forest = self.underground.areas[4]
        deep_forest.assign_room_numbers(12)
    
    def dig_river(self):
        river = self.underground.areas[5]
        river.assign_room_numbers(16)
    
    def dig_meadows(self):
        meadows = self.underground.areas[6]
        meadows.assign_room_numbers(0)

        spider_room = self.underground.get_room_of_number(0)
        spider_cave_exit = [
            [-2, -1, -2],
            [30, 7, 30],
            [30, 30, 30],
            [30, 30, 30]
        ]
        spider_cave_warp = Presence(trigger_on_contact=True)
        spider_cave_warp.add_warp("overworld", 6, 0, -1)
        spider_cave = KeyObject(length=3, height=4,
                                presence=spider_cave_warp, presence_x=1, presence_y=1,
                                override_terrain=spider_cave_exit)
        spider_room.location.add_key_object(spider_cave)
    
    def dig_hills(self):
        hills = self.underground.areas[7]
        hills.assign_room_numbers(8)
    
    def dig_lakeside(self):
        lakeside = self.underground.areas[8]
        lakeside.assign_room_numbers(20)