from blueprint import Blueprint
from maze import Maze
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
            Location.MOUNTAIN: pygame.image.load("resources/obstacles/Green_rock_2.png"),
            Location.WATER: pygame.image.load("resources/obstacles/Water_2.png"),
            Location.FENCE: None,
            Location.ROAD: None
        }
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Random RPG")
        self.clock = pygame.time.Clock()
        self.running = True

    def new_game(self):
        blueprint = Blueprint.main_map_blueprint()
        print(blueprint.get_layout())
        # Something's wrong with the randomization, connections are not respected
        # randomized_blueprint = blueprint.randomize_areas()
        # print(randomized_blueprint.get_layout())
        maze = Maze(3, 3)
        maze.build_maze(blueprint)
        self.maze = maze.copy()
        
        for tries in range(10):
            try:
                self.maze.construct_connections()
                self.maze.exchange_rooms()
                self.maze.start_trails()
                self.maze.construct_areas()
                break
            except Exception as e:
                print(f"Attempt {tries} failed: {e}")
                self.maze = maze.copy()
        
        print(self.maze.get_layout())

        for room in self.maze.rooms:
            room.create_location(self.GRID_SIZE, self.GRID_SIZE, 3)

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif not self.player:
                    break
                elif event.key == pygame.K_w:
                    if self.transition_check(self.player.x, self.player.y - 1):
                        self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.NORTH))
                        self.player.y = self.GRID_SIZE - 1
                    elif not self.collision_check(self.player.x, self.player.y - 1):
                        self.player.start_movement((0, -1))
                elif event.key == pygame.K_s:
                    if self.transition_check(self.player.x, self.player.y + 1):
                        self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.SOUTH))
                        self.player.y = 0
                    elif not self.collision_check(self.player.x, self.player.y + 1):
                        self.player.start_movement((0, 1))
                elif event.key == pygame.K_a:
                    if self.transition_check(self.player.x - 1, self.player.y):
                        self.set_room(self.maze.get_next_location(self.current_room.x, self.current_room.y, Room.WEST))
                        self.player.x = self.GRID_SIZE - 1
                    elif not self.collision_check(self.player.x - 1, self.player.y):
                        self.player.start_movement((-1, 0))
                elif event.key == pygame.K_d:
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

