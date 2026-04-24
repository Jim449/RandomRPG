from blueprint import Blueprint
from area import Area
from maze import Maze
from location import Location, KeyObject
from unit import Unit, Presence
from room import Room
from combat_input import CombatInput
from adventure_menu import AdventureMenu
from combat import Combat
from quest_log import QuestLog
from animation_handler import AnimationHandler
from mechanics.characterStats import CharacterStats
from storage import Storage
from mechanics.inventory import Inventory
from random import randrange
from animation import TextAscendAnimation, FadeAnimation, TextWriteAnimation, WalkDownAnimation, WalkUpAnimation, BlinkAnimation
from user_interface import UserInterface
from encounter import Encounter
from map_builder import MapBuilder
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
            Location.MUSHROOMS: pygame.image.load("resources/obstacles/Large_mushroom.png"),
            Location.BRIGHT_GREEN_ROCK: pygame.image.load("resources/obstacles/Bright_green_rock.png"),
            Location.PALE_GREEN_ROCK: pygame.image.load("resources/obstacles/Pale_green_rock.png"),
            Location.MOUNTAIN: pygame.image.load("resources/obstacles/Green_rock.png"),
            Location.MOUNTAIN_ENTRANCE: pygame.image.load("resources/obstacles/Green_rock_entrance.png"),
            Location.MOUNTAIN_EXIT: pygame.image.load("resources/obstacles/Green_rock_exit.png"),
            Location.WATER: pygame.image.load("resources/obstacles/Water.png"),
            Location.PURPLE_WATER: pygame.image.load("resources/obstacles/Purple_water.png"),
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
            self.TERRAIN[Location.PURPLE_WATER + i + 1] = pygame.image.load(f"resources/obstacles/Purple_water_{dir}.png")

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
        map_builder = MapBuilder(self.storage)
        map_builder.build()
        
        self.maze = map_builder.maze
        self.underground_maze = map_builder.underground
        self.current_maze = self.maze
        self.quest_log = QuestLog()
        self.set_room(self.maze.get_room_of_number(2))
        
        print(f"Current room: {(self.current_room.x, self.current_room.y)}")

        # Add the player
        start_position = self.current_location.get_random_position()
        self.player = Unit("Hero", sprite=pygame.image.load("resources/people/Player_small.png"),
                           team=1, grid_x=start_position[0], grid_y=start_position[1])
        hero_stats = {"Strength": 4, "Defense": 0, "Resistance": 0,
                      "Agility": 3, "Intelligence": 0, "Stamina": 0,
                      "Rank": 6, "Constitution": 4}
        self.player.set_stats(CharacterStats(hero_stats))
        self.inventory = Inventory()
        self.inventory.add_item(self.storage.get_item("Herb"))
        self.adventure_menu = AdventureMenu(self.player, self.inventory)
    
    def load_sprite(self, presence: Presence):
        """Loads a sprite"""
        if presence.sprite_path:
            presence.sprite = pygame.image.load(presence.sprite_path)
    
    def load_conversations(self, presence: Presence):
        """Loads all conversations belonging to a presence"""
        if presence.conversations:
            return
        for name, index in presence.conversation_names:
            presence.add_conversation(self.storage.get_conversation(name, index))
    
    def set_room(self, room: Room):
        """Sets the current room and prepare sprites for display"""
        self.current_room = room
        self.current_location = room.location
        self.current_area = self.current_maze.areas[room.area]

        for presence in room.location.presences:
            # Need to load conversations first since they may affect sprite visibility
            self.load_conversations(presence)
            if presence.should_show(self.quest_log):
                self.load_sprite(presence)
            
    
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
            if presence.grid_y == y and presence.sprite:
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

