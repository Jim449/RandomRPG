from blueprint import Blueprint
from area import Area
from maze import Maze, IllegalMazeError
from location import Location
from player import Player
from room import Room
import pygame
import sys

class Game():
    def __init__(self):
        self.maze = None
        self.current_room = None
        self.current_location = None
        self.player = None

        # Pygame settings
        self.CELL_SIZE = 32
        self.GRID_SIZE = 15
        self.FPS = 30
        self.SCREEN_WIDTH = self.GRID_SIZE * self.CELL_SIZE
        self.SCREEN_HEIGHT = self.GRID_SIZE * self.CELL_SIZE
        
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
    
    def load_images(self):
        directions = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
        
        for i, dir in enumerate(directions):
            self.TERRAIN[Location.MOUNTAIN + i + 1] = pygame.image.load(f"resources/obstacles/Green_rock_{dir}.png")
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
        # Something's wrong with the randomization, connections are not respected
        # randomized_blueprint = blueprint.randomize_areas()
        # print(randomized_blueprint.get_layout())

        area_0 = Area(0,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.FENCE, Location.FOREST),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.2, 0.4),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=4,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
        area_1 = Area(1,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.FENCE, Location.FOREST),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.1, 0.3),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=0,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
        area_2 = Area(2,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.FOREST),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.1, 0.3),
                      large_obstacles=(Location.WATER,),
                      large_obstacle_amount=3,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=2)
        
        area_3 = Area(3,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.FOREST, Location.FENCE),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.0, 0.2),
                      large_obstacles=(Location.MOUNTAIN, Location.WATER),
                      large_obstacle_amount=2,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=3)
        
        area_4 = Area(4,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.WATER, Location.FOREST),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.3, 0.5),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=0,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=5)
        
        area_5 = Area(5,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.WATER, Location.FENCE, Location.FOREST),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.2, 0.4),
                      large_obstacles=(Location.WATER,),
                      large_obstacle_amount=3,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=4)
        
        area_6 = Area(6,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.WATER, Location.FOREST),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.4, 0.6),
                      large_obstacles=(Location.MOUNTAIN, Location.WATER),
                      large_obstacle_amount=1,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=1)
        
        area_7 = Area(7,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.WATER, Location.FOREST),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.3, 0.5),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=2,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=2)
        
        area_8 = Area(8,
                      base_tile=Location.GRASS,
                      allowed_obstacles=(Location.MOUNTAIN, Location.FOREST),
                      pool_terrain_chance=0.5,
                      pool_terrain_growth=(0, 4),
                      line_terrain_chance=0.5,
                      line_terrain_amount=(1, 3),
                      obstacle_coverage=(0.2, 0.4),
                      large_obstacles=(Location.MOUNTAIN,),
                      large_obstacle_amount=4,
                      base_inaccessible_tile=Location.WATER,
                      inaccessible_tile_amount=0)
        
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

        self.current_room = self.maze.get_random_location()
        print(f"Current room: {(self.current_room.x, self.current_room.y)}")
        self.current_location = self.current_room.location
        
        halfpoint = (self.GRID_SIZE - 1) // 2
        for coordinates in ((halfpoint, 0), (halfpoint, self.GRID_SIZE - 1), (0, halfpoint), (self.GRID_SIZE - 1, halfpoint)):
            if self.current_location.get_terrain(coordinates[0], coordinates[1]) <= 0:
                self.player = Player(coordinates[0], coordinates[1])
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
        
        # Handle continuous movement
        if self.player and not self.player.moving:
            keys = pygame.key.get_pressed()
            
            # Check for speed boost
            speed_boost = keys[pygame.K_p]
            if speed_boost != self.player.speed_boost:
                self.player.set_speed_boost(speed_boost)
            
            # Handle movement keys
            if keys[pygame.K_w]:
                if self.transition_check(self.player.x, self.player.y - 1):
                    self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.NORTH))
                    self.player.y = self.GRID_SIZE - 1
                elif not self.collision_check(self.player.x, self.player.y - 1):
                    self.player.start_movement((0, -1))
            elif keys[pygame.K_s]:
                if self.transition_check(self.player.x, self.player.y + 1):
                    self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.SOUTH))
                    self.player.y = 0
                elif not self.collision_check(self.player.x, self.player.y + 1):
                    self.player.start_movement((0, 1))
            elif keys[pygame.K_a]:
                if self.transition_check(self.player.x - 1, self.player.y):
                    self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.WEST))
                    self.player.x = self.GRID_SIZE - 1
                elif not self.collision_check(self.player.x - 1, self.player.y):
                    self.player.start_movement((-1, 0))
            elif keys[pygame.K_d]:
                if self.transition_check(self.player.x + 1, self.player.y):
                    self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.EAST))
                    self.player.x = 0
                elif not self.collision_check(self.player.x + 1, self.player.y):
                    self.player.start_movement((1, 0))

    def draw_location(self):
        """Draw the current location terrain on screen"""
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
            self.screen.blit(self.player.sprite, (self.player.x * self.CELL_SIZE + self.player.x_offset, self.player.y * self.CELL_SIZE + self.player.y_offset))

    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            self.handle_events()
            
            if self.player:
                self.player.move()
            
            # Draw everything
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

