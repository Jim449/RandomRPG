from blueprint import Blueprint
from area import Area
from maze import Maze, IllegalMazeError
from location import Location, KeyObject
from unit import Unit, Presence
from room import Room
from combat_input import CombatInput
from adventure_menu import AdventureMenu
from combat import Combat
from conversation import Conversation
from quest_log import QuestLog
from animation_handler import AnimationHandler
from mechanics.characterStats import CharacterStats
from storage import Storage
from mechanics.inventory import Inventory
from random import randrange
from animation import TextAscendAnimation, FadeAnimation, TextWriteAnimation, WalkDownAnimation, WalkUpAnimation, BlinkAnimation
from user_interface import UserInterface
from encounter import Encounter
import pygame
import sys

class Game():
    def __init__(self):
        # Pygame settings
        self.CELL_SIZE = 32
        self.GRID_SIZE = 15
        self.FPS = 30
        self.FADEOUT_SPEED = 8
        self.SCREEN_WIDTH = self.GRID_SIZE * self.CELL_SIZE
        self.SCREEN_HEIGHT = self.GRID_SIZE * self.CELL_SIZE
        self.COMBAT_MAP = pygame.image.load("resources/backgrounds/Plains.png")
        self.POINTER = pygame.image.load("resources/other/Pointer.png")
        self.TEXT_SPEED = 2

        # Consider adding to storage, add dynamic loading
        self.maze = None
        self.underground_maze = None

        # Need to change variable names if I want to use current_maze instead of maze
        self.current_maze = None
        self.current_room = None
        self.current_location = None
        self.current_area = None
        self.player = None
        self.quest_log = None
        self.combat = None
        self.combat_input = None
        self.adventure_menu = None
        self.conversation = None
        self.encounter = None
        self.inventory = None
        self.triggered_presence = None
        self.storage = Storage()
        self.animation_handler = AnimationHandler()
        self.fadeout = 0
        self.fadeout_direction = 0
        self.encounter_interval = (10, 40)
        self.encounter_countdown = randrange(self.encounter_interval[0], self.encounter_interval[1])
        self.fade = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.fade.fill((0, 0, 0, 0))
        
        self.TERRAIN = {
            Location.GRASS: pygame.image.load("resources/tiles/Grass_2.png"),
            Location.PALE_GRASS: pygame.image.load("resources/obstacles/Pale_grass.png"),
            Location.FOREST: pygame.image.load("resources/obstacles/Forest_3.png"),
            Location.BRIGHT_GREEN_ROCK: pygame.image.load("resources/obstacles/Bright_green_rock.png"),
            Location.PALE_GREEN_ROCK: pygame.image.load("resources/obstacles/Pale_green_rock.png"),
            Location.MOUNTAIN: pygame.image.load("resources/obstacles/Green_rock.png"),
            Location.MOUNTAIN_ENTRANCE: pygame.image.load("resources/obstacles/Green_rock_entrance.png"),
            Location.MOUNTAIN_EXIT: pygame.image.load("resources/obstacles/Green_rock_exit.png"),
            Location.WATER: pygame.image.load("resources/obstacles/Water.png"),
            Location.FENCE_H: pygame.image.load("resources/obstacles/Fence_H.png"),
            Location.FENCE_V: pygame.image.load("resources/obstacles/Fence_V.png"),
            Location.OAK: pygame.image.load("resources/obstacles/Oak_ABOVE.png"),
            Location.HOUSE_3x2: pygame.image.load("resources/obstacles/House_3x2_ORANGE.png"),
            Location.BRIDGE_H: None,
            Location.BRIDGE_V: None
        }
        self.load_images()

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Random RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        self.user_interface = UserInterface(self.screen)
        
        # Initialize font for UI
        self.font = pygame.font.Font(None, 24)
        self.combat_font = pygame.font.Font(None, 16)
        self.health_font = pygame.font.Font(None, 24)
        self.ui_background_color = (0, 0, 0, 180)  # Semi-transparent black
        self.ui_text_color = (255, 255, 255)  # White text
    
    def load_images(self):
        directions = ("N", "NE", "E", "SE", "S", "SW", "W", "NW", "I_NE", "I_SE", "I_SW", "I_NW", "DES", "ASC")
        
        for i, dir in enumerate(directions):
            self.TERRAIN[Location.MOUNTAIN + i + 1] = pygame.image.load(f"resources/obstacles/Green_rock_{dir}.png")
            self.TERRAIN[Location.WATER + i + 1] = pygame.image.load(f"resources/obstacles/Water_{dir}.png")

        for i, dir in enumerate(directions[:8]):
            try:
                self.TERRAIN[Location.BRIDGE_H + i + 1] = pygame.image.load(f"resources/obstacles/Bridge_H_{dir}.png")
            except FileNotFoundError:
                pass
            try:
                self.TERRAIN[Location.BRIDGE_V + i + 1] = pygame.image.load(f"resources/obstacles/Bridge_V_{dir}.png")
            except FileNotFoundError:
                pass
    
    def define_main_map(self):
        """Defines the main map."""
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

        great_mountains = self.maze.areas[0]
        highlands = self.maze.areas[1]
        coastline = self.maze.areas[2]
        forest = self.maze.areas[3]
        deep_forest = self.maze.areas[4]
        river = self.maze.areas[5]
        meadows = self.maze.areas[6]
        hills = self.maze.areas[7]
        lakeside = self.maze.areas[8]

        # Assign room numbers so that I can override room settings
        # Rooms connecting to other areas get specific room numbers
        self.maze.clear_room_numbers()
        
        meadows.get_connecting_room(forest.id).number = 0
        meadows.get_connecting_room(hills.id).number = 1
        meadows.assign_room_numbers(2)

        forest.get_connecting_room(meadows.id).number = 9
        forest.get_connecting_room(deep_forest.id).number = 10
        forest.assign_room_numbers(11)

        hills.get_connecting_room(meadows.id).number = 18
        hills.get_connecting_room(deep_forest.id).number = 19
        hills.get_connecting_room(lakeside.id).number = 20
        hills.assign_room_numbers(21)

        deep_forest.get_connecting_room(forest.id).number = 27
        deep_forest.get_connecting_room(hills.id).number = 28
        deep_forest.get_connecting_room(river.id).number = 29
        deep_forest.get_connecting_room(highlands.id).number = 30
        deep_forest.assign_room_numbers(31)
        
        river.get_connecting_room(deep_forest.id).number = 36
        river.get_connecting_room(lakeside.id).number = 37
        river.get_connecting_room(coastline.id).number = 38
        river.assign_room_numbers(39)

        lakeside.get_connecting_room(hills.id).number = 45
        lakeside.get_connecting_room(river.id).number = 46
        lakeside.assign_room_numbers(47)

        coastline.get_connecting_room(river.id).number = 54
        coastline.assign_room_numbers(55)

        highlands.get_connecting_room(deep_forest.id).number = 63
        highlands.get_connecting_room(great_mountains.id).number = 64
        highlands.assign_room_numbers(65)

        great_mountains.get_connecting_room(highlands.id).number = 72
        great_mountains.assign_room_numbers(73)

        # Starting room, a safe zone with healing NPCs
        village_room = self.maze.get_room_of_number(2)

        village_room.location.safe_zone = True
        village_room.line_terrain_amount = (3, 3)
        village_room.pool_terrain_amount = (0, 0)

        # Isabel
        # She'll have to do without a name variable
        innkeeper = Presence(sprite=pygame.image.load("resources/people/Commoner_female.png"))
        innkeeper.add_conversation(self.storage.get_conversation("the_innkeeper"))
        innkeeper.add_conversation(self.storage.get_conversation("the_wolf", 3))

        inn = KeyObject(length=3, height=3, terrain=Location.HOUSE_3x2,
                        presence=innkeeper, presence_x=1, presence_y=2,
                        entrance_type=Location.IMPORTANT_BLOCKING,
                        entrance_x=1, entrance_y=2)
        village_room.location.add_key_object(inn)

        # Henry
        blacksmith = Presence(sprite=pygame.image.load("resources/people/Commoner_male.png"))
        blacksmith.add_conversation(self.storage.get_conversation("the_blacksmith"))
        blacksmith.add_conversation(self.storage.get_conversation("the_hunters_cabin", 0))
        blacksmith.add_conversation(self.storage.get_conversation("the_hunters_cabin", 1))
        for conversation in self.storage.get_conversations("the_blacksmith_shop"):
            blacksmith.add_conversation(conversation)

        smithy = KeyObject(length=3, height=3, terrain=Location.HOUSE_3x2,
                           presence=blacksmith, presence_x=1, presence_y=2,
                           entrance_type=Location.IMPORTANT_BLOCKING,
                           entrance_x=1, entrance_y=2)
        village_room.location.add_key_object(smithy)

        # Eliza
        herbalist = Presence(sprite=pygame.image.load("resources/people/Commoner_female.png"))
        herbalist.add_conversation(self.storage.get_conversation("the_herbalist"))
        herbalist.add_conversation(self.storage.get_conversation("the_herbalists_gift", 0))
        herbalist.add_conversation(self.storage.get_conversation("the_druids_blade", 1))
        
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
        hunter = Presence(sprite=pygame.image.load("resources/people/Commoner_male.png"))
        hunter.add_conversation(self.storage.get_conversation("the_hunter"))
        hunter.add_conversation(self.storage.get_conversation("the_hunters_cabin", 2))
        hunter.add_conversation(self.storage.get_conversation("the_wolf", 0))
        hunter.add_conversation(self.storage.get_conversation("the_wolf", 1))
        hunter.add_conversation(self.storage.get_conversation("the_wolf", 2))

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

        crescent_knife = Presence()
        crescent_knife.add_conversation(self.storage.get_conversation("the_druids_blade", 0))

        oak_terrain = [
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, 10, 9, -1, -1, -1],
            [-1, -1, -1, 9, 9, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
        ]

        the_oak = KeyObject(length=8, height=8,
                            presence=crescent_knife, presence_x=4, presence_y=4,
                            override_terrain=oak_terrain)
        great_oak_room.location.add_key_object(the_oak)

        # Witch house in the forest
        # Hands out a quest and sells spells
        witches_room = self.maze.get_room_of_number(11)
        witches_room.location.min_obstacle_coverage = 0.5
        witches_room.location.max_obstacle_coverage = 0.5
        witches_room.location.line_terrain_amount = (0, 0)
        witches_room.location.pool_terrain_amount = (1, 1)

        witch = Presence(sprite=pygame.image.load("resources/people/Commoner_female.png"))
        witch.add_conversation(self.storage.get_conversation("the_witch"))
        witch.add_conversation(self.storage.get_conversation("the_witches_house", 0))
        witch.add_conversation(self.storage.get_conversation("the_witches_house", 2))
        witch.add_conversation(self.storage.get_conversation("the_witches_house", 3))

        witches_house = KeyObject(length=3, height=3, terrain=Location.HOUSE_3x2,
                                  presence=witch, presence_x=1, presence_y=2,
                                  entrance_type=Location.IMPORTANT_BLOCKING,
                                  entrance_x=1, entrance_y=2)
        witches_room.location.add_key_object(witches_house)

        goblin_room = self.maze.get_room_of_number(12)
        goblin_room.location.allowed_obstacles = (Location.FOREST, Location.MOUNTAIN, Location.OAK)
        goblin_cave_terrain = [
            [30, 30, 30],
            [30, 30, 30],
            [30, 6, 30],
            [1, -1, 1]
        ]
        # We're going underground!
        cave_warp = Presence(trigger_on_contact=True)
        cave_warp.add_warp("underground", 4, 0, 1)

        goblin_cave = KeyObject(length=3, height=4,
                                presence=cave_warp, presence_x=1, presence_y=2,
                                override_terrain=goblin_cave_terrain)
        goblin_room.location.add_key_object(goblin_cave)

        # Build the locations
        self.maze.build_locations()

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
        allowed_obstacles=(Location.MOUNTAIN, Location.WATER),
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

        self.underground_maze = Maze(3, 2, "underground")
        for area in (area_0, area_1, area_2, area_3, area_4, area_5, area_6, area_7, area_8):
            self.underground_maze.add_area(area)

        self.underground_maze.build_maze(underground_blueprint)
        print(self.underground_maze.get_layout())

        for room in self.underground_maze.rooms:
            for direction in range(4):
                room.set_terrain(direction, Location.MOUNTAIN)

        self.underground_maze.setup_locations()

        great_mountains = self.underground_maze.areas[0]
        highlands = self.underground_maze.areas[1]
        coastline = self.underground_maze.areas[2]
        forest = self.underground_maze.areas[3]
        deep_forest = self.underground_maze.areas[4]
        river = self.underground_maze.areas[5]
        meadows = self.underground_maze.areas[6]
        hills = self.underground_maze.areas[7]
        lakeside = self.underground_maze.areas[8]

        self.underground_maze.clear_room_numbers()

        meadows.assign_room_numbers(0)
        forest.assign_room_numbers(4)
        hills.assign_room_numbers(8)
        deep_forest.assign_room_numbers(12)
        river.assign_room_numbers(16)
        lakeside.assign_room_numbers(20)
        coastline.assign_room_numbers(24)
        highlands.assign_room_numbers(28)
        great_mountains.assign_room_numbers(32)

        goblin_room = self.underground_maze.get_room_of_number(4)
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

        self.underground_maze.build_locations()

    def new_game(self):
        self.define_main_map()
        self.define_underground_map()
        
        self.current_maze = self.maze
        self.current_room = self.maze.get_room_of_number(3)
        self.current_location = self.current_room.location
        self.current_area = self.maze.areas[self.current_room.area]
        
        print(f"Current room: {(self.current_room.x, self.current_room.y)}")

        # Add the player
        start_position = self.current_location.get_random_position()
        self.player = Unit("Hero", pygame.image.load("resources/people/Player_small.png"),
                           team=1, grid_x=start_position[0], grid_y=start_position[1])
        hero_stats = {"Strength": 4, "Defense": 0, "Resistance": 0,
                      "Agility": 3, "Intelligence": 0, "Stamina": 0,
                      "Rank": 4, "Constitution": 6}
        self.player.set_stats(CharacterStats(hero_stats))
        self.inventory = Inventory()
        self.inventory.add_item(self.storage.get_item("Herb"))
        self.quest_log = QuestLog()
        self.adventure_menu = AdventureMenu(self.player, self.inventory)
    
    def set_room(self, room: Room):
        self.current_room = room
        self.current_location = room.location
        self.current_area = self.current_maze.areas[room.area]
    
    def warp_to(self, map: str, room_number: int):
        """Warps the player to a different map."""
        last_map = self.current_maze.name
        last_room_number = self.current_room.number

        if map == "overworld":
            self.current_maze = self.maze
        elif map == "underground":
            self.current_maze = self.underground_maze
        
        self.current_room = self.current_maze.get_room_of_number(room_number)
        self.current_location = self.current_room.location
        self.current_area = self.current_maze.areas[self.current_room.area]

        for presence in self.current_location.presences:
            if presence.is_matching_warp(last_map, last_room_number):
                self.player.set_grid_position(*presence.get_exit_position())
                return

    def transition_check(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.GRID_SIZE or y < 0 or y >= self.GRID_SIZE:
            return True
        else:
            return False

    def collision_check(self, x: int, y: int) -> bool:
        """Returns True if the tile is impassable.
        If there is a presence on the tile,
        attempts to start a conversation.
        If a conversation starts, tile is treated as impassable."""
        presence = self.current_location.get_presence_at(x, y)

        if presence and presence.trigger_on_contact:
            print(f"Triggering presence at {x}, {y}")

            self.conversation = self.quest_log.get_conversation(presence.conversations)

            if self.conversation:
                self.triggered_presence = presence
                self.start_conversation()
                return True
            elif presence.is_warp():
                self.warp_to(presence.warp_map, presence.warp_room_number)
                return True
        return not self.current_location.get_passable(x, y)
    
    def investigate(self, x: int, y: int) -> bool:
        """Attempts to start a conversation with a nearby presence.
        Should be call from the players grid position.
        The player doesn't have to face the presence.
        Returns True if a conversation starts."""
        presence = self.current_location.get_nearby_presence(x, y)
        
        if presence and not presence.trigger_on_contact:
            self.conversation = self.quest_log.get_conversation(presence.conversations)
            
            if self.conversation:
                self.triggered_presence = presence
                self.start_conversation()
                return True
        return False

    def handle_events(self):
        """Handle pygame events"""
        # Handle window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Handle combat input
                if self.combat:
                    self.handle_combat_input(event.key)
                    return
                elif self.conversation:
                    self.handle_conversation_input(event.key)
                    return
                elif self.adventure_menu.is_active():
                    self.handle_adventure_menu_input(event.key)
                    return
                # Handle other key presses when not in combat/conversation/menu
                elif event.key == pygame.K_l:
                    self.investigate(self.player.grid_x, self.player.grid_y)
                elif event.key == pygame.K_RETURN:
                    self.adventure_menu.set_mode(AdventureMenu.MENU)
        
        # Handle continuous movement (only when not in combat)
        if self.player and not self.player.moving \
            and not self.combat and not self.conversation \
            and not self.adventure_menu.is_active():
            keys = pygame.key.get_pressed()
            
            # Check for speed boost
            speed_boost = keys[pygame.K_p]
            if speed_boost != self.player.speed_boost:
                self.player.set_speed_boost(speed_boost)
            
            # Handle movement keys
            if keys[pygame.K_w]:
                if self.transition_check(self.player.grid_x, self.player.grid_y - 1):
                    self.set_room(self.current_maze.get_next_location(self.current_room.x, self.current_room.y, Room.NORTH))
                    self.player.set_grid_position(y=self.GRID_SIZE - 1)
                elif not self.collision_check(self.player.grid_x, self.player.grid_y - 1):
                    self.player.start_movement((0, -1))
            elif keys[pygame.K_s]:
                if self.transition_check(self.player.grid_x, self.player.grid_y + 1):
                    self.set_room(self.current_maze.get_next_location(self.current_room.x, self.current_room.y, Room.SOUTH))
                    self.player.set_grid_position(y=0)
                elif not self.collision_check(self.player.grid_x, self.player.grid_y + 1):
                    self.player.start_movement((0, 1))
            elif keys[pygame.K_a]:
                if self.transition_check(self.player.grid_x - 1, self.player.grid_y):
                    self.set_room(self.current_maze.get_next_location(self.current_room.x, self.current_room.y, Room.WEST))
                    self.player.set_grid_position(x=self.GRID_SIZE - 1)
                elif not self.collision_check(self.player.grid_x - 1, self.player.grid_y):
                    self.player.start_movement((-1, 0))
            elif keys[pygame.K_d]:
                if self.transition_check(self.player.grid_x + 1, self.player.grid_y):
                    self.set_room(self.current_maze.get_next_location(self.current_room.x, self.current_room.y, Room.EAST))
                    self.player.set_grid_position(x=0)
                elif not self.collision_check(self.player.grid_x + 1, self.player.grid_y):
                    self.player.start_movement((1, 0))

    def escape_combat(self):
        """Escapes the combat"""
        animation = FadeAnimation(self.fade,
                                  start_alpha=0,
                                  end_alpha=255,
                                  speed=8,
                                  callback=self.escape_encounter)
        self.animation_handler.add_animation(animation)
    
    def display_combat_message(self, message: list[str]):
        self.combat_input.set_message(message)
        animation = TextWriteAnimation(self.user_interface,
                                       self.combat_input.get_message(),
                                       self.font,
                                       speed=self.TEXT_SPEED,
                                       delay=60)
        self.animation_handler.add_animation(animation)

    def handle_combat_input(self, key):
        """Handle keyboard input during combat"""
        
        mode = self.combat_input.get_mode()
        
        # Navigation keys
        if key == pygame.K_UP or key == pygame.K_w:
            self.combat_input.increase_y(-1)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.combat_input.increase_y(1)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.combat_input.increase_x(-1)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.combat_input.increase_x(1)
        
        # Action keys
        elif key == pygame.K_l:
            if mode == CombatInput.MENU:
                choice = self.combat_input.get_menu_choice()
                if choice == "Attack":
                    self.player.selected_action = self.storage.get_action("Attack")
                    self.combat_input.set_mode(CombatInput.TARGETING)
                    print("Attack selected")
                elif choice == "Defend":
                    self.combat.select_action(self.storage.get_action("Defend"), self.player)
                    self.combat_input.set_mode(CombatInput.INACTIVE)
                elif choice == "Cast spell":
                    self.combat_input.set_mode(CombatInput.SPELL_SELECT)
                elif choice == "Run":
                    if self.encounter.block_escape:
                        self.display_combat_message(["Failed to escape."])
                    elif self.encounter.allow_escape or self.combat.escape_check():
                        self.escape_combat()
                    else:
                        self.display_combat_message(["Failed to escape."])
                        # Since escape rate is so low, allow the player to act again
                        # This means I cannot redo the escape roll
                        # self.combat.select_action(self.storage.get_action("Inaction"), self.player)
                        # self.combat_input.set_mode(CombatInput.INACTIVE)
            elif mode == CombatInput.TARGETING:
                enemy = self.combat_input.get_enemy()
                if enemy:
                    print(f"Attacking enemy at position ({enemy.x}, {enemy.y})")
                    self.combat.select_action(self.player.selected_action, enemy)
                    self.combat_input.set_mode(CombatInput.INACTIVE)
                else:
                    self.combat_input.undo_mode()
            elif mode == CombatInput.SPELL_SELECT:
                spell = self.combat_input.get_spell_choice()
                if spell:
                    print(f"Selected spell: {spell}")
                    # TODO: Implement spell casting logic
                    self.combat_input.undo_mode()
                else:
                    self.combat_input.undo_mode()
        
        # Back/Cancel key
        elif key == pygame.K_p:
            self.combat_input.undo_mode()

    def handle_adventure_menu_input(self, key):
        """Handle keyboard input during adventure menu"""

        mode = self.adventure_menu.get_mode()
        
        # Navigation keys
        if key == pygame.K_UP or key == pygame.K_w:
            self.adventure_menu.increase_y(-1)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.adventure_menu.increase_y(1)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.adventure_menu.increase_x(-1)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.adventure_menu.increase_x(1)
        elif key == pygame.K_p:
            self.adventure_menu.undo_mode()
        elif key == pygame.K_RETURN:
            self.adventure_menu.set_mode(AdventureMenu.INACTIVE)

        elif key == pygame.K_l:
            if mode == AdventureMenu.MENU:
                choice = self.adventure_menu.get_menu_choice()
                if choice == "Inventory":
                    self.adventure_menu.open_inventory()
                    self.adventure_menu.load_equipment()
                elif choice == "Exit menu":
                    self.adventure_menu.set_mode(AdventureMenu.INACTIVE)
            elif mode == AdventureMenu.INVENTORY:
                self.adventure_menu.set_mode(AdventureMenu.ITEM_DETAILS)
            elif mode == AdventureMenu.ITEM_DETAILS:
                item_choice = self.adventure_menu.get_item_choice()
                if item_choice == "Equip":
                    self.inventory.equip(self.player, self.adventure_menu.get_selected_item())
                    self.adventure_menu.load_equipment()
                    self.adventure_menu.undo_mode()
                elif item_choice == "Use":
                    index = self.adventure_menu.get_item_index()
                    message = self.inventory.use_item(index, self.player)
                    if message:
                        # Go back two steps and reopen inventory
                        # in order to update the item display
                        self.adventure_menu.undo_mode()
                        self.adventure_menu.undo_mode()
                        self.adventure_menu.open_inventory()
                        self.player.update_display()
                elif item_choice == "Cancel":
                    self.adventure_menu.undo_mode()

    def handle_conversation_input(self, key):
        """Handle keyboard input during conversation"""
        if self.conversation.awaiting_confirmation():
            if key in (pygame.K_w, pygame.K_s):
                self.conversation.increase_confirmation_y()
            elif (key == pygame.K_l and self.conversation.get_confirmation_y() == 0):
                if self.inventory.coins >= self.conversation.cost:
                    self.inventory.remove_coins(self.conversation.cost)
                    self.end_conversation()
                else:
                    # Run the reject conversation since there are no "can't afford it"-conversations yet
                    self.conversation.reset()
                    self.conversation = self.conversation.reject_conversation
                    self.start_conversation()
            elif (key == pygame.K_l and self.conversation.get_confirmation_y() == 1) \
                or key == pygame.K_p:
                self.conversation.reset()
                self.conversation = self.conversation.reject_conversation
                self.start_conversation()
            return
        
        elif key in (pygame.K_l, pygame.K_p):
            if self.animation_handler.has_animations():
                self.animation_handler.end_all()
                return
            
            message = self.conversation.get_message()
            
            if message:
                animation = TextWriteAnimation(self.user_interface, message, self.font,
                                               speed=self.TEXT_SPEED)
                self.animation_handler.add_animation(animation)
            else:
                self.end_conversation()
    
    def start_conversation(self):
        """Gets the first conversation message and starts writing animation"""
        message = self.conversation.get_message()
        animation = TextWriteAnimation(self.user_interface, message, self.font,
                                       speed=self.TEXT_SPEED)
        self.animation_handler.add_animation(animation)

    def end_conversation(self):
        """Ends the conversation and handles rewards"""
        if self.conversation.heal:
            self.player.full_heal()
        if self.conversation.restore:
            self.player.full_restore()
        if self.conversation.item:
            self.inventory.add_item(self.storage.get_item(self.conversation.item),
                                    equip_to=self.player)
        if self.conversation.reward:
            self.inventory.add_coins(self.conversation.reward)
        self.quest_log.finish_conversation(self.conversation)
        self.conversation.reset()

        if self.conversation.accept_conversation:
            self.conversation = self.conversation.accept_conversation
            self.start_conversation()
        else:
            self.conversation = None

    def process_combat(self):
        """Process combat logic and handle animations."""
        if self.animation_handler.has_animations():
            pass
        elif self.combat_input.get_mode() == CombatInput.MESSAGE:
            message = self.combat_input.get_message()
            if message:
                animation = TextWriteAnimation(self.user_interface,
                                               message,
                                               self.font,
                                               speed=self.TEXT_SPEED,
                                               delay=60)
                self.animation_handler.add_animation(animation)
        elif self.combat.phase == Combat.PHASE_VICTORY:
            animation = FadeAnimation(
                self.fade,
                start_alpha=0,
                end_alpha=255,
                speed=8,
                callback=self.end_encounter)
            self.animation_handler.add_animation(animation)

        elif self.combat.phase == Combat.PHASE_DEFEAT:
            # I don't have a main menu yet
            # Just fade to black and end the game
            # It doesn't work though, I do need a main menu
            self.combat.phase = Combat.PHASE_VOID
            animation = FadeAnimation(
                self.fade,
                start_alpha=0,
                end_alpha=255,
                speed=4)
            self.animation_handler.add_animation(animation)
        elif self.combat.has_defeated_units():
            for unit in self.combat.defeated_units:
                animation = FadeAnimation(
                    unit,
                    start_alpha=255,
                    end_alpha=0,
                    speed=8,
                    callback=lambda: self.combat.remove_unit(unit))
                self.animation_handler.add_animation(animation)
        elif self.combat_input.get_mode() == CombatInput.INACTIVE:
            self.combat.process_turn()

            if self.combat.active_unit and self.combat.active_unit.team == 0:
                forward_animation = WalkDownAnimation(self.combat.active_unit)
                backward_animation = WalkUpAnimation(self.combat.active_unit)

                if self.player.health_change < 0:
                    damage_animation = TextAscendAnimation(
                        self.screen,
                        40,
                        300,
                        f"{-self.player.health_change}",
                        font=self.health_font,
                        color=(255, 0, 0),
                        speed=2,
                        fadeout=8)
                    self.animation_handler.chain_animations(forward_animation, [backward_animation, damage_animation])
                    self.player.display_health += self.player.health_change
                    self.player.health_change = 0
                else:
                    self.animation_handler.chain_animations(forward_animation, [backward_animation])

                self.player.display_health = min(self.player.display_health, self.player.get_final_stat("MaxHealth"))
            
            elif self.combat.active_unit and self.combat.active_unit.team == 1:
                damage_animations = []
                blink_animations = []

                for target in self.combat.current_targets:
                    if target.health_change < 0:
                        health_color = (255, 0, 0)
                        blink_animations.append(BlinkAnimation(target))
                    elif target.health_change > 0:
                        health_color = (0, 255, 0)
                    else:
                        continue
                    damage_animations.append(TextAscendAnimation(
                        self.screen,
                        target.x + 32,
                        target.y,
                        f"{-target.health_change}",
                        font=self.health_font,
                        color=health_color,
                        speed=2,
                        fadeout=8))
                    target.display_health += target.health_change
                    target.health_change = 0
                # This will make everyone blink at the same time
                # but the damage animations will have random delays
                # If it doesn't look good, I have to pair the animations up
                # Too bad I don't have an AOE attack yet
                self.animation_handler.add_multiple_animations(blink_animations, spacing=0)
                self.animation_handler.add_multiple_animations(damage_animations, spacing=5)

    def draw_combat(self):
        """Draws the combat map"""
        self.screen.blit(self.COMBAT_MAP, (0, 0))

        for enemy in self.combat_input.get_enemy_list():
            self.screen.blit(enemy.get_sprite(), enemy.get_position())
            enemy.get_sprite().set_alpha(enemy.get_alpha())
        
        self.screen.blit(self.fade, (0, 0))
        self.user_interface.draw_main_panel()
        self.user_interface.draw_health_and_magic(self.player)

        if self.combat_input.get_mode() == CombatInput.MESSAGE:
            self.user_interface.draw_message_panel(self.user_interface.full_message_panel)
            return

        if self.combat_input.has_mode(CombatInput.MENU):
            self.user_interface.draw_left_panel(self.combat_input.menu_options,
                                                self.combat_input.menu_y)
        if self.combat_input.has_mode(CombatInput.SPELL_SELECT):
            self.user_interface.draw_spell_panel(self.combat_input.spell_options,
                                                 self.combat_input.submenu_x,
                                                 self.combat_input.submenu_y)
        if self.combat_input.get_mode() == CombatInput.TARGETING:
            self.user_interface.draw_pointer(self.combat_input)
        elif self.combat_input.get_mode() == CombatInput.MASS_TARGETING:
            self.user_interface.draw_mass_pointers(self.combat_input)

    def draw_sprites(self, y: int):
        for presence in self.current_location.presences:
            if presence.is_visible() and presence.grid_y == y:
                self.screen.blit(presence.sprite, presence.get_position())
                presence.sprite.set_alpha(presence.get_alpha())

    def draw_location(self):
        """Draws the current location terrain on screen"""
        if not self.current_location:
            return
        
        base_tile = self.TERRAIN[self.current_location.base_tile]
        invisible_tiles = (Location.ANONYMOUS_BLOCKING, Location.IMPORTANT_PASSABLE,
                           Location.UNREACHABLE_PASSABLE, Location.REGULAR_PASSABLE,
                           Location.IMPORTANT_BLOCKING)

        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                self.screen.blit(base_tile, (x * self.CELL_SIZE, y * self.CELL_SIZE))
        
        for y in range(self.GRID_SIZE):
            self.draw_sprites(y)

            if self.player and self.player.grid_y == y:
                self.screen.blit(self.player.sprite, self.player.get_position())
                self.player.sprite.set_alpha(self.player.get_alpha())

            for x in range(self.GRID_SIZE):
                terrain = self.current_location.terrain[y][x]
                
                if terrain in invisible_tiles or terrain == self.current_location.base_tile:
                    pass
                else:
                    self.screen.blit(self.TERRAIN[terrain], (x * self.CELL_SIZE, y * self.CELL_SIZE))

        if self.conversation:
            self.user_interface.draw_main_panel()
            
            if self.conversation.awaiting_confirmation():
                self.user_interface.draw_message_panel(self.user_interface.message_panel)
                self.user_interface.draw_confirmation_panel(self.conversation.prompt, self.conversation.confirmation_y)
            else:
                self.user_interface.draw_message_panel(self.user_interface.full_message_panel)
        elif self.adventure_menu.is_active():
            self.user_interface.draw_main_panel()
            self.user_interface.draw_overview(self.player, self.current_area.name)

            if self.adventure_menu.get_mode() == AdventureMenu.MENU:
                self.user_interface.draw_left_box(self.adventure_menu.menu_options,
                                                  self.adventure_menu.menu_x,
                                                  self.adventure_menu.menu_y)
            elif self.adventure_menu.has_mode(AdventureMenu.INVENTORY):
                self.user_interface.draw_spell_panel(self.adventure_menu.items,
                                                  self.adventure_menu.submenu_x,
                                                  self.adventure_menu.submenu_y)
                self.user_interface.draw_info_panel(self.adventure_menu.get_equipment_info())

                if self.adventure_menu.has_mode(AdventureMenu.ITEM_DETAILS):
                    self.user_interface.draw_left_panel(self.adventure_menu.item_options,
                                                        self.adventure_menu.details_y)

    def start_encounter(self, encounter: Encounter):
        self.encounter = encounter.instantiate(self.storage)
        self.combat_input = CombatInput(self.player, self.encounter.units)
        # Set test spells for now
        self.combat_input.set_spells(["Fireball", "Heal"])
        self.combat = Combat(self.combat_input)
        
        animation = FadeAnimation(
            self.fade,
            start_alpha=255,
            end_alpha=0,
            speed=8)
        self.animation_handler.add_animation(animation)
        
    def end_encounter(self):
        self.encounter.finish_encounter(self.quest_log)
        # Not the best place for this
        # but it'll do for now
        self.player.gain_experience(self.encounter.get_experience())
        self.inventory.add_coins(self.encounter.get_coins())
        self.combat = None
    
    def escape_encounter(self):
        self.combat = None

    def tick_encounter(self):
        if self.current_location.safe_zone:
            return
        else:
            self.encounter_countdown -= 1
        
        if self.encounter_countdown <= 0:
            self.encounter_countdown = randrange(self.encounter_interval[0], self.encounter_interval[1])
            self.start_encounter(self.current_area.get_encounter(self.quest_log))
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            if self.player:
                if self.player.move():
                    self.tick_encounter()
                    
            if self.combat:
                self.process_combat()
                self.draw_combat()
                self.animation_handler.update()
            elif self.conversation:
                self.animation_handler.update()
                self.draw_location()
            else:
                self.draw_location()
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(self.FPS)
        
        # Cleanup
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.new_game()
    game.run()

