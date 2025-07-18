from blueprint import Blueprint
from area import Area
from maze import Maze, IllegalMazeError
from location import Location
from unit import Unit, Presence
from room import Room
from combat_input import CombatInput
from adventure_menu import AdventureMenu
from combat import Combat
from conversation import Conversation
from quest_log import QuestLog, Quest
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

        self.maze = None
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
        self.storage = Storage()
        self.animation_handler = AnimationHandler()
        self.fadeout = 0
        self.fadeout_direction = 0
        self.encounter_interval = (10, 30)
        self.encounter_countdown = randrange(self.encounter_interval[0], self.encounter_interval[1])
        self.fade = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.fade.fill((0, 0, 0, 0))
        
        self.TERRAIN = {
            Location.GRASS: pygame.image.load("resources/tiles/Grass_2.png"),
            Location.FOREST: pygame.image.load("resources/obstacles/Forest_3.png"),
            Location.MOUNTAIN: pygame.image.load("resources/obstacles/Green_rock.png"),
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
            
    def new_game(self):
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
                      base_tile=Location.GRASS,
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
        area_4.add_encounter(Encounter(["Red_spider", "Red_spider", "Red_spider", "Red_spider", "Red_spider", "Red_spider"], [1, 1, 1, 1, 1, 1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Black_bat", "Black_bat"], [1, 1], encounter_weight=1))
        area_4.add_encounter(Encounter(["Black_bat", "Black_bat", "Black_bat", "Black_bat"], [1, 1, 1, 1], encounter_weight=1))
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
        area_6.add_encounter(Encounter(["Red_spider"], [1], encounter_weight=3))
        area_6.add_encounter(Encounter(["Red_spider", "Red_spider"], [1, 1], encounter_weight=3))
        area_6.add_encounter(Encounter(["Goblin"], [1], encounter_weight=3, reward=5))
        # Maybe a quest encounter?
        conversation = Conversation([])
        conversation.add_quest("The wolf", 2, progress_quest=True)
        area_6.add_encounter(Encounter(["Gray_wolf"], [1], encounter_weight=1, conversation=conversation))
        
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
        
        maze = Maze(3, 3)
        for area in (area_0, area_1, area_2, area_3, area_4, area_5, area_6, area_7, area_8):
            maze.add_area(area)

        maze.build_maze(blueprint)
        self.maze = maze.copy()
        
        for tries in range(10):
            try:
                self.maze.construct_connections()
                # self.maze.exchange_rooms()
                self.maze.start_trails()
                self.maze.construct_areas()
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
        # I may want to create single-entrance rooms
        # and assign specific room numbers to them
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
        self.current_room = self.maze.get_room_of_number(2)
        self.current_location = self.current_room.location
        self.current_area = self.maze.areas[self.current_room.area]
        
        print(f"Current room: {(self.current_room.x, self.current_room.y)}")

        self.current_room.location.safe_zone = True
        self.current_location.line_terrain_amount = (3, 3)
        self.current_location.pool_terrain_amount = (0, 0)
        self.current_location.allowed_obstacles.remove(Location.OAK)
        self.current_location.allowed_obstacles.append(Location.HOUSE_3x2)
        self.current_location.object_terrain_amount = (4, 4)

        # Isabel
        # She'll have to do without a name variable
        innkeeper = Presence(sprite=pygame.image.load("resources/people/Commoner_female.png"))
        innkeeper_offer = Conversation(["Good day, traveler. You look weary.", "Let me heal your wounds."])
        innkeeper_offer.add_reward(heal=True, restore=True)
        innkeeper.add_conversation(innkeeper_offer)

        # Henry
        blacksmith = Presence(sprite=pygame.image.load("resources/people/Commoner_male.png"))
        blacksmith_business = Conversation(["Hello there!",
                                            "I have a fine sabre for sale.",
                                            "It's yours for 100 coins."])
        blacksmith_business.add_quest("The blacksmith", 0)
        blacksmith_purchase = Conversation(["Much appreciated.\nI'm sure it'll serve you well."])
        blacksmith_purchase.add_reward(item="Sabre")
        blacksmith_refusal = Conversation(["Is it too expensive?",
                                           "I've heard the goblins out in the meadows\ncarry a lot of coins on them."])
        blacksmith_business.add_accept_conversation(blacksmith_purchase, "Buy item?", cost=100)
        blacksmith_business.add_reject_conversation(blacksmith_refusal)
        blacksmith.add_conversation(blacksmith_business)

        blacksmith_further_business = Conversation(["Hello there!",
                                                    "Would you like to buy this fine chainmail?",
                                                    "It'll cost 400 coins."])
        blacksmith_further_business.add_quest("The blacksmith", 1)
        blacksmith_further_purchase = Conversation(["Thank you.\nI'm quite confident in it."])
        blacksmith_further_refusal = Conversation(["Don't be like that.\nYou need a good armor."])
        blacksmith_further_business.add_accept_conversation(blacksmith_further_purchase, "Buy item?", cost=400)
        blacksmith_further_business.add_reject_conversation(blacksmith_further_refusal)
        blacksmith.add_conversation(blacksmith_further_business)

        blacksmith_quest = Conversation(["Hey there.\nYou're a traveler?",
                                         "Lately, the meadow's been infested with spiders.\nStay safe out there.",
                                         "I'm getting a bit worried about our hunter.\nHe lives alone in a cabin.",
                                         "Can you carry a message to him?\nI'm sure he'll reward you\nfor your troubles.",
                                         "Excellent!\nHis cabin is in the meadows."])
        blacksmith_quest.add_quest("The hunter", 0)
        blacksmith.add_conversation(blacksmith_quest)

        # Eliza
        herbalist = Presence(sprite=pygame.image.load("resources/people/Commoner_female.png"))
        herbalist_offer = Conversation(["Good day.",
                                           "Are you interested in buying\nsome healing herbs?",
                                           "It's 10 coins for one handful."])
        herbalist_purchase = Conversation(["Excellent. Here you go."])
        herbalist_purchase.add_reward(item="Herb")
        herbalist_refusal = Conversation(["That's too bad.\nThey're really effective."])
        herbalist_offer.add_accept_conversation(herbalist_purchase, "Buy item?", cost=10)
        herbalist_offer.add_reject_conversation(herbalist_refusal)
        herbalist.add_conversation(herbalist_offer)
        
        herbalist_gift = Conversation(["Good day.\nAre you going out into the wilderness?",
                                       "Here, take this herb.\nIt'll keep you healthy.",
                                       "If you need another one, come talk with me.\nI'll have to charge you, though."])
        herbalist_gift.add_reward(item="Herb")
        herbalist_gift.add_quest("The herbalist", 0)
        herbalist.add_conversation(herbalist_gift)

        self.current_location.presences.append(innkeeper)
        self.current_location.presences.append(blacksmith)
        self.current_location.presences.append(herbalist)
        
        # Hunters cabin. Hands out quests
        hunter_room = self.maze.get_room_of_number(3)
        hunter_room.location.line_terrain_amount = (2, 2)
        hunter_room.location.pool_terrain_amount = (1, 1)
        hunter_room.location.allowed_obstacles.remove(Location.OAK)
        hunter_room.location.allowed_obstacles.append(Location.HOUSE_3x2)
        hunter_room.location.object_terrain_amount = (1, 1)

        # Richard
        hunter = Presence(sprite=pygame.image.load("resources/people/Commoner_male.png"))
        hunter_greeting = Conversation(["Good day."])
        hunter.add_conversation(hunter_greeting)

        hunter_response = Conversation(["A message from the village?",
                                        "Those spiders are a nuisance\nbut I can handle them just fine.",
                                        "Anyways, it's dangerous out here.\nYou'll need a weapon.",
                                        "This is the Silkcutter.\nYou'll feel nimbler when you use it.",
                                        "You must be tired.\nTake a rest before you leave."])
        hunter_response.add_quest("The hunter", 1, quest_initiation="The wolf")
        hunter_response.add_reward(item="Silkcutter", heal=True, restore=True)
        hunter.add_conversation(hunter_response)

        hunter_offer = Conversation(["Lately, a vicious wolf\nhas been attacking the farmers.",
                                     "If you can slay it,\nI'll give you a reward.",
                                     "I don't know where it is.\nIf you wander around long enough,\nit'll find you."])
        hunter_offer.add_quest("The wolf", 1, progress_quest=True)
        hunter.add_conversation(hunter_offer)

        hunter_reward = Conversation(["So you slayed that damned wolf.",
                                      "Here, take this quarterstaff.\nIt's great for blocking enemy blows.",
                                      "I'll give you some coins as well."])
        hunter_reward.add_quest("The wolf", 3, progress_quest=True)
        hunter_reward.add_reward(item="Quarterstaff", reward=30)
        hunter.add_conversation(hunter_reward)

        hunter_room.location.presences.append(hunter)

        # Build the locations
        self.maze.build_locations()

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
        self.current_area = self.maze.areas[room.area]

    def transition_check(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.GRID_SIZE or y < 0 or y >= self.GRID_SIZE:
            return True
        else:
            return False

    def collision_check(self, x: int, y: int) -> bool:
        return not self.current_location.get_passable(x, y)

    def handle_events(self):
        """Handle pygame events"""
        # Handle window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Handle combat input
                elif self.combat:
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
                    npc = self.current_location.get_nearby_presence(self.player.grid_x, self.player.grid_y)
                    if npc and not self.conversation:
                        self.conversation = self.quest_log.get_conversation(npc.conversations)
                        self.start_conversation()
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
                    self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.NORTH))
                    self.player.set_grid_position(y=self.GRID_SIZE - 1)
                elif not self.collision_check(self.player.grid_x, self.player.grid_y - 1):
                    self.player.start_movement((0, -1))
            elif keys[pygame.K_s]:
                if self.transition_check(self.player.grid_x, self.player.grid_y + 1):
                    self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.SOUTH))
                    self.player.set_grid_position(y=0)
                elif not self.collision_check(self.player.grid_x, self.player.grid_y + 1):
                    self.player.start_movement((0, 1))
            elif keys[pygame.K_a]:
                if self.transition_check(self.player.grid_x - 1, self.player.grid_y):
                    self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.WEST))
                    self.player.set_grid_position(x=self.GRID_SIZE - 1)
                elif not self.collision_check(self.player.grid_x - 1, self.player.grid_y):
                    self.player.start_movement((-1, 0))
            elif keys[pygame.K_d]:
                if self.transition_check(self.player.grid_x + 1, self.player.grid_y):
                    self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.EAST))
                    self.player.set_grid_position(x=0)
                elif not self.collision_check(self.player.grid_x + 1, self.player.grid_y):
                    self.player.start_movement((1, 0))

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
                    if not self.encounter.allow_escape:
                        print("No escape allowed")
                        # I should print a message to the user
                        # Allow the player to select another action
                    if self.combat.escape_check():
                        animation = FadeAnimation(self.fade,
                                                start_alpha=0,
                                                end_alpha=255,
                                                speed=8,
                                                callback=self.escape_encounter)
                        self.animation_handler.add_animation(animation)
                    else:
                        print("Failed to escape")
                        self.combat.select_action(self.storage.get_action("Inaction"), self.player)
                        self.combat_input.set_mode(CombatInput.INACTIVE)
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
        # elif self.combat.phase == Combat.PHASE_FADEOUT:
        #     # Do nothing until the fadeout is complete
        #     # I may change how the fadeout works later
        #     pass
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

            # Hopefully, these animations should look good
            # They don't cover all cases
            # but at this point, everyone's using basic attacks all the time
            if self.combat.active_unit and self.combat.active_unit.team == 0:
                forward_animation = WalkDownAnimation(self.combat.active_unit)
                backward_animation = WalkUpAnimation(self.combat.active_unit)

                # TODO: I should move that combat ui to the user_interface
                # and set a proper position for the health text
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

        # I may want to draw some messages
        # I need a condition to check if there are messages
        # self.user_interface.draw_message_panel()

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

    def draw_location(self):
        """Draws the current location terrain on screen"""
        if not self.current_location:
            return
        
        base_tile = self.TERRAIN[self.current_location.base_tile]

        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                self.screen.blit(base_tile, (x * self.CELL_SIZE, y * self.CELL_SIZE))
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                terrain = self.current_location.terrain[y][x]
                
                if terrain == Location.SPRITE_STATION:
                    presence = self.current_location.get_presence_at(x, y)
                    if presence.sprite:
                        self.screen.blit(presence.sprite, presence.get_position())
                elif terrain in (Location.ANONYMOUS_BLOCKING, Location.ANONYMOUS_ENTRANCE):
                    pass
                elif terrain != self.current_location.base_tile:
                    # I need to add passable terrain first, not here
                    # Otherwise I get a "dig-into-the-ground"-bug
                    self.screen.blit(self.TERRAIN[terrain], (x * self.CELL_SIZE, y * self.CELL_SIZE))
            
            if self.player and self.player.grid_y == y:
                self.screen.blit(self.player.sprite, self.player.get_position())
                self.player.sprite.set_alpha(self.player.get_alpha())
        
        # self.user_interface.draw_overview(self.player, self.current_area.name)

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

    def start_encounter(self):
        self.encounter = self.current_area.get_encounter(self.quest_log)
        self.encounter = self.encounter.instantiate(self.storage)
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
            self.start_encounter()
    
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

