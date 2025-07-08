from blueprint import Blueprint
from area import Area
from maze import Maze, IllegalMazeError
from location import Location
from unit import Unit
from room import Room
from combat_input import CombatInput
from combat import Combat
from animation_handler import AnimationHandler
from mechanics.characterStats import CharacterStats
from mechanics.storage import Storage
from random import randrange
from animation import TextAscendAnimation, FadeAnimation
import pygame
import sys

class Game():
    def __init__(self):
        # Pygame settings
        self.CELL_SIZE = 32
        self.GRID_SIZE = 15
        self.FPS = 30
        self.FADEOUT_SPEED = 5
        self.SCREEN_WIDTH = self.GRID_SIZE * self.CELL_SIZE
        self.SCREEN_HEIGHT = self.GRID_SIZE * self.CELL_SIZE
        self.COMBAT_MAP = pygame.image.load("resources/backgrounds/Plains.png")
        self.POINTER = pygame.image.load("resources/other/Pointer.png")

        self.maze = None
        self.current_room = None
        self.current_location = None
        self.player = None
        self.combat = None
        self.combat_input = None
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
            Location.FENCE: pygame.image.load("resources/obstacles/Fence.png"),
            Location.BRIDGE_H: None,
            Location.BRIDGE_V: None,
            Location.ROAD: None
        }
        self.load_images()

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Random RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        
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
                      allowed_obstacles=(Location.WATER, Location.FOREST, Location.FENCE),
                      pool_terrain_amount=(-1, 2),
                      pool_terrain_growth=(0, 10),
                      line_terrain_amount=(-1, 3),
                      large_obstacle_growth=(0, 0),
                      obstacle_coverage=(0.1, 0.2),
                      large_obstacles=tuple(),
                      large_obstacle_amount=0,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
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
        
        self.maze.place_large_obstacles()
        self.maze.place_inaccessible_tiles()
        self.maze.construct_locations()
        print(self.maze.get_layout())

        # self.current_room = self.maze.get_location(0, 0)
        self.current_room = self.maze.get_random_location()
        print(f"Current room: {(self.current_room.x, self.current_room.y)}")
        self.current_location = self.current_room.location
        
        halfpoint = (self.GRID_SIZE - 1) // 2
        for coordinates in ((halfpoint, 0), (halfpoint, self.GRID_SIZE - 1), (0, halfpoint), (self.GRID_SIZE - 1, halfpoint)):
            if self.current_location.get_terrain(coordinates[0], coordinates[1]) <= 0:
                self.player = Unit("Hero", pygame.image.load("resources/people/player_small.png"),
                                   team=1, grid_x=coordinates[0], grid_y=coordinates[1])
                hero_stats = {"Strength": 4, "Defense": 0, "Resistance": 0,
                              "Agility": 3, "Intelligence": 0, "Stamina": 0,
                              "Rank": 4, "Constitution": 6}
                self.player.set_stats(CharacterStats(hero_stats))
                break
    
    def set_room(self, room: Room):
        self.current_room = room
        self.current_location = room.location

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
        
        # Handle continuous movement (only when not in combat)
        if self.player and not self.player.moving and not self.combat:
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
                    # TODO: Implement defend action
                    print("Defend selected")
                elif choice == "Cast spell":
                    self.combat_input.set_mode(CombatInput.SPELL_SELECT)
                elif choice == "Run":
                    # TODO: Implement run action
                    print("Run selected")
                    self.end_encounter()
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

    def process_combat(self):
        """Process combat logic and handle animations."""
        if self.animation_handler.has_animations():
            pass
        elif self.combat.phase == Combat.PHASE_FADEOUT:
            # Do nothing until the fadeout is complete
            # I may change how the fadeout works later
            pass
        elif self.combat.phase == Combat.PHASE_VICTORY:
            print("Start combat fadeout")
            self.combat.phase = Combat.PHASE_FADEOUT
            self.end_encounter()
        elif self.combat.phase == Combat.PHASE_DEFEAT:
            # TODO: Implement defeat logic
            # For now, I'll just let the game run forever
            pass
        elif self.combat.has_defeated_units():
            for unit in self.combat.defeated_units:
                animation = FadeAnimation(
                    unit,
                    start_alpha=255,
                    end_alpha=0,
                    speed=4,
                    callback=lambda: self.combat.remove_unit(unit))
                self.animation_handler.add_animation(animation)
        elif self.combat_input.get_mode() == CombatInput.INACTIVE:
            self.combat.process_turn()

            # This will do for now but I need to determine
            # which animations to play, if any
            if self.combat.active_unit:
                # Create an action animation (attack, spell cast, etc.)
                action_animation_duration = 30  # 1 second at 30 FPS
                self.animation_handler.create_idle_animation(
                    duration_frames=action_animation_duration)
            # TODO: I'm adding a health change animation here
            # but it's a bit too early.
            # I should wait until the action animation is complete
            
            for target in self.combat.current_targets:
                if target.health_change < 0:
                    health_color = (255, 0, 0)
                elif target.health_change > 0:
                    health_color = (0, 255, 0)
                else:
                    continue
                animation = TextAscendAnimation(
                    self.screen,
                    target.x + 32,
                    target.y,
                    f"{-target.health_change}",
                    font=self.health_font,
                    color=health_color,
                    speed=2,
                    fadeout=10)
                self.animation_handler.add_animation(animation)
                target.display_health += target.health_change
                target.health_change = 0

    def draw_combat_ui(self):
        """Draw the combat UI window at the bottom of the screen"""
        if not self.combat_input or self.combat_input.get_mode() in (CombatInput.PREPARATION, CombatInput.CLEANUP):
            return
        
        # UI dimensions
        ui_width = 480
        ui_height = 128
        ui_x = 0
        ui_y = self.SCREEN_HEIGHT - ui_height
        
        # Menu subwindow dimensions  
        menu_subwindow_width = 80
        menu_subwindow_height = ui_height
        menu_subwindow_x = ui_x
        menu_subwindow_y = ui_y
        
        # Spell subwindow dimensions
        spell_subwindow_width = 320
        spell_subwindow_height = ui_height
        spell_subwindow_x = menu_subwindow_x + menu_subwindow_width
        spell_subwindow_y = ui_y
        
        # Colors
        ui_bg_color = (40, 40, 40, 200)  # Dark gray with transparency
        subwindow_bg_color = (20, 20, 20, 220)  # Darker gray
        text_color = (255, 255, 255)  # White
        health_color = (0, 0, 0)
        highlight_color = (100, 150, 255)  # Light blue for selected option
        
        # Draw main UI background
        ui_surface = pygame.Surface((ui_width, ui_height), pygame.SRCALPHA)
        ui_surface.fill(ui_bg_color)
        self.screen.blit(ui_surface, (ui_x, ui_y))
        
        # Draw menu subwindow background
        menu_subwindow_surface = pygame.Surface((menu_subwindow_width, menu_subwindow_height), pygame.SRCALPHA)
        menu_subwindow_surface.fill(subwindow_bg_color)
        self.screen.blit(menu_subwindow_surface, (menu_subwindow_x, menu_subwindow_y))
        
        if self.combat_input.get_mode() == CombatInput.TARGETING:
            self.screen.blit(self.POINTER, self.combat_input.get_target_pointer())
        elif self.combat_input.get_mode() == CombatInput.MASS_TARGETING:
            for pointer in self.combat_input.get_mass_pointers():
                self.screen.blit(self.POINTER, pointer)
        
        health_text = self.health_font.render(f"HP {self.player.display_health} / {self.player.get_final_stat("MaxHealth")}", True, health_color)
        magic_text = self.health_font.render(f"MP {self.player.get_final_stat("Magic")} / {self.player.get_final_stat("MaxMagic")}", True, health_color)
        self.screen.blit(health_text, (20, ui_y - 20))
        self.screen.blit(magic_text, (400, ui_y - 20))

        # Draw menu options in the menu subwindow
        if self.combat_input.has_mode(CombatInput.MENU):
            menu_options = self.combat_input.menu_options
            selected_index = self.combat_input.menu_y
            
            # Calculate text positioning
            text_start_y = menu_subwindow_y + 10
            line_height = 25
            text_margin = 5
            
            for i, option in enumerate(menu_options):
                # Determine text color based on selection
                current_text_color = highlight_color if i == selected_index else text_color
                
                # Render text
                text_surface = self.combat_font.render(option, True, current_text_color)
                text_y = text_start_y + (i * line_height)
                
                # Draw selection background for highlighted option
                if i == selected_index:
                    selection_rect = pygame.Rect(menu_subwindow_x + 2, text_y - 2, menu_subwindow_width - 4, line_height - 2)
                    pygame.draw.rect(self.screen, (50, 80, 150, 100), selection_rect)
                
                # Draw text
                self.screen.blit(text_surface, (menu_subwindow_x + text_margin, text_y))
        
        # Draw spell subwindow if spell selection is active
        if self.combat_input.has_mode(CombatInput.SPELL_SELECT):
            # Draw spell subwindow background
            spell_subwindow_surface = pygame.Surface((spell_subwindow_width, spell_subwindow_height), pygame.SRCALPHA)
            spell_subwindow_surface.fill(subwindow_bg_color)
            self.screen.blit(spell_subwindow_surface, (spell_subwindow_x, spell_subwindow_y))
            
            # Get spell options and selection
            spell_options = self.combat_input.spell_options
            selected_x = self.combat_input.submenu_x
            selected_y = self.combat_input.submenu_y
            
            # Calculate grid layout
            grid_cols = 4
            grid_rows = 4
            cell_width = (spell_subwindow_width - 20) // grid_cols  # 20px total margin
            cell_height = (spell_subwindow_height - 20) // grid_rows  # 20px total margin
            start_x = spell_subwindow_x + 10
            start_y = spell_subwindow_y + 10
            
            # Draw spell grid
            for row in range(grid_rows):
                for col in range(grid_cols):
                    spell_name = spell_options[row][col]
                    
                    # Calculate cell position
                    cell_x = start_x + (col * cell_width)
                    cell_y = start_y + (row * cell_height)
                    
                    # Determine if this cell is selected
                    is_selected = (col == selected_x and row == selected_y)
                    
                    # Draw selection background for highlighted spell
                    if is_selected:
                        selection_rect = pygame.Rect(cell_x, cell_y, cell_width - 2, cell_height - 2)
                        pygame.draw.rect(self.screen, (50, 80, 150, 100), selection_rect)
                    
                    # Draw spell name if it exists
                    if spell_name:
                        # Determine text color
                        current_text_color = highlight_color if is_selected else text_color
                        
                        # Render text (truncate if too long)
                        display_name = spell_name
                        if len(display_name) > 10:  # Adjust based on cell width
                            display_name = display_name[:7] + "..."
                        
                        text_surface = self.combat_font.render(display_name, True, current_text_color)
                        
                        # Center text in cell
                        text_x = cell_x + (cell_width - text_surface.get_width()) // 2
                        text_y = cell_y + (cell_height - text_surface.get_height()) // 2
                        
                        self.screen.blit(text_surface, (text_x, text_y))

    def draw_combat(self):
        """Draws the combat map"""
        self.screen.blit(self.COMBAT_MAP, (0, 0))

        for enemy in self.combat_input.get_enemy_list():
            self.screen.blit(enemy.sprite, enemy.get_position())
            enemy.sprite.set_alpha(enemy.get_alpha())

        if self.fadeout_direction != 0:
            self.fade.set_alpha(self.fadeout)
            self.screen.blit(self.fade, (0, 0))
            
            if self.fadeout == 0:
                self.combat_input.set_mode(CombatInput.INACTIVE)
                self.fadeout_direction = 0
            elif self.fadeout == 255:
                self.combat = None
                self.fadeout_direction = 0
        
        # Draw combat UI
        self.draw_combat_ui()

    def draw_location(self):
        """Draws the current location terrain on screen"""
        if not self.current_location:
            return
        
        # Draw each cell
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                terrain_type = self.current_location.terrain[y][x]
                
                pixel_x = x * self.CELL_SIZE
                pixel_y = y * self.CELL_SIZE
                self.screen.blit(self.TERRAIN[Location.GRASS], (pixel_x, pixel_y))
                image = self.TERRAIN[terrain_type]

                if image:
                    self.screen.blit(self.TERRAIN[terrain_type], (pixel_x, pixel_y))

        if self.player:
            self.screen.blit(self.player.sprite, self.player.get_position())
        
        self.draw_ui()

        if self.fadeout_direction != 0:
            self.fade.set_alpha(self.fadeout)
            self.screen.blit(self.fade, (0, 0))

    def draw_ui(self):
        """Draw UI elements like area name and room coordinates"""
        if not self.current_room:
            return

        area = self.maze.areas[self.current_room.area]
        area_name = area.name
        room_coords = f"Room ({self.current_room.x}, {self.current_room.y})"
        
        area_text = self.font.render(area_name, True, self.ui_text_color)
        coords_text = self.font.render(room_coords, True, self.ui_text_color)
        
        max_width = max(area_text.get_width(), coords_text.get_width())
        total_height = area_text.get_height() + coords_text.get_height() + 10  # 10px padding
        
        # Position in top right corner with some margin
        margin = 10
        bg_x = self.SCREEN_WIDTH - max_width - margin * 2
        bg_y = margin
        
        # Create semi-transparent background surface
        background = pygame.Surface((max_width + margin * 2, total_height), pygame.SRCALPHA)
        background.fill(self.ui_background_color)
        
        # Blit background
        self.screen.blit(background, (bg_x, bg_y))
        
        # Blit text
        text_x = bg_x + margin
        area_y = bg_y + margin // 2
        coords_y = area_y + area_text.get_height() + 5
        
        self.screen.blit(area_text, (text_x, area_y))
        self.screen.blit(coords_text, (text_x, coords_y))

    def encounter(self):
        # Create some enemies at random
        enemy_count = randrange(1, 7)
        enemies = []
        spider_stats = {"Strength": 4, "Defense": 0, "Resistance": 0,
                        "Agility": 3, "Intelligence": 0, "Stamina": 0,
                        "Rank": 4, "Constitution": 1}
        for i in range(enemy_count):
            enemy = Unit("Red spider", pygame.image.load("resources/enemies/Red_spider.png"), team=0)
            enemy.set_stats(CharacterStats(spider_stats))
            enemy.add_action(self.storage.get_action("Attack"))
            enemies.append(enemy)
        
        self.combat_input = CombatInput(self.player, enemies)
        self.combat_input.set_spells(["Fireball", "Heal"])
        self.combat = Combat(self.combat_input)
        # That should be enough for now. Replace with something more robust later

        self.fadeout_direction = -1
        self.fadeout = 255 + self.FADEOUT_SPEED * self.fadeout_direction
    
    def end_encounter(self):
        # Fades out the combat screen
        # Combat will end in draw_combat when fadeout is complete
        # I should add some victory text before this
        self.combat_input.set_mode(CombatInput.CLEANUP)
        self.fadeout_direction = 1
        self.fadeout = 0 + self.FADEOUT_SPEED * self.fadeout_direction

    def tick_encounter(self):
        self.encounter_countdown -= 1
        if self.encounter_countdown <= 0:
            self.encounter_countdown = randrange(self.encounter_interval[0], self.encounter_interval[1])
            self.encounter()
    
    def tick_fadeout(self):
        self.fadeout += self.FADEOUT_SPEED * self.fadeout_direction
        if self.fadeout < 0:
            self.fadeout = 0
        elif self.fadeout > 255:
            self.fadeout = 255

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            if self.player:
                if self.player.move():
                    self.tick_encounter()
            
            if self.fadeout_direction != 0:
                self.tick_fadeout()
            
            if self.combat:
                self.process_combat()
                self.draw_combat()
                self.animation_handler.update()
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

