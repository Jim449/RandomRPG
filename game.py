from blueprint import Blueprint
from maze import Maze
from location import Location
import pygame
import sys

class Game():
    def __init__(self):
        self.maze = None
        self.current_room = None
        self.current_location = None
        
        # Pygame settings
        self.CELL_SIZE = 32
        self.GRID_SIZE = 15
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

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

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
                

    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            self.handle_events()
            
            # Draw everything
            self.draw_location()
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(60)  # 60 FPS
        
        # Cleanup
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.new_game()
    game.run()

