import random
from collections import deque

class Location():
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    # Terrain types
    ROAD = -1
    GRASS = 0
    FOREST = 1
    MOUNTAIN = 2
    WATER = 3
    FENCE = 4

    """Describes a location in the maze"""
    def __init__(self, room, width: int = 15, height: int = 15, gap: int = 3):
        self.terrain = [[0 for x in range(width)] for y in range(height)]
        self.width = width
        self.height = height
        self.create_edges(room, gap)
        
        # Random check to add mountain terrain near center
        if random.random() < 0.3:
            self.add_center_mountains()
        
        self.expand_terrain_pools()
        
        # Create some trees which the fences can collide with
        # But not so many, that'd make the fences too short
        self.create_obstacles(room, 0.1)
        self.create_fences()
        obstacle_percentage = self.calculate_safe_obstacle_percentage(0.5)
        self.create_obstacles(room, obstacle_percentage)
    
    def create_edges(self, room, gap: int) -> None:
        """Creates edges around the room"""
        for x in range(self.width // 2):
            self.terrain[0][x] = room.terrain[Location.WEST]
            self.terrain[self.height - 1][x] = room.terrain[Location.SOUTH]
        for y in range(self.height // 2):
            self.terrain[y][0] = room.terrain[Location.WEST]
            self.terrain[y][self.width - 1] = room.terrain[Location.NORTH]
        for x in range(self.width // 2, self.width):
            self.terrain[0][x] = room.terrain[Location.NORTH]
            self.terrain[self.height - 1][x] = room.terrain[Location.EAST]
        for y in range(self.height // 2, self.height):
            self.terrain[y][0] = room.terrain[Location.SOUTH]
            self.terrain[y][self.width - 1] = room.terrain[Location.EAST]
        
        start_x_gap = (self.width - gap) // 2
        start_y_gap = (self.height - gap) // 2

        for x in range(start_x_gap, start_x_gap + gap):
            if room.paths[Location.NORTH] == 1:
                self.terrain[0][x] = Location.ROAD
            if room.paths[Location.SOUTH] == 1:
                self.terrain[self.height - 1][x] = Location.ROAD

        for y in range(start_y_gap, start_y_gap + gap):
            if room.paths[Location.WEST] == 1:
                self.terrain[y][0] = Location.ROAD
            if room.paths[Location.EAST] == 1:
                self.terrain[y][self.width - 1] = Location.ROAD

    @staticmethod
    def is_passable(type: int) -> bool:
        return type <= 0
    
    def add_center_mountains(self) -> None:
        """Adds mountain terrain near the center of the location"""
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Try to place a 2x2 mountain pool near center
        # Add some randomness to the exact position
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        
        mountain_x = max(1, min(self.width - 3, center_x + offset_x))
        mountain_y = max(1, min(self.height - 3, center_y + offset_y))
        
        # Place initial mountain terrain (2x2 block)
        mountain_coords = [
            (mountain_x, mountain_y),
            (mountain_x + 1, mountain_y),
            (mountain_x, mountain_y + 1),
            (mountain_x + 1, mountain_y + 1)
        ]
        
        # Check if placement is valid (all positions are passable)
        can_place = True
        for x, y in mountain_coords:
            if not self.is_passable(self.terrain[y][x]):
                can_place = False
                break
        
        if can_place:
            for x, y in mountain_coords:
                self.terrain[y][x] = Location.MOUNTAIN
            self.expand_from_edge(mountain_x, mountain_y, Location.MOUNTAIN,
                                  min_expansions=0, max_expansions=8)
    
    def calculate_safe_obstacle_percentage(self, max_total_coverage: float = 0.5) -> float:
        """Calculates a safe obstacle percentage to prevent over-crowding"""
        total_cells = self.width * self.height
        non_passable_cells = 0
        
        # Count current non-passable terrain
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_passable(self.terrain[y][x]):
                    non_passable_cells += 1
        
        current_coverage = non_passable_cells / total_cells
        
        # If we're already at or above the limit, don't add more obstacles
        if current_coverage >= max_total_coverage:
            return 0.0
        
        # Calculate how much space is available for additional obstacles
        remaining_coverage = max_total_coverage - current_coverage
        
        # Calculate interior passable cells for percentage calculation
        interior_passable_cells = 0
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.is_passable(self.terrain[y][x]):
                    interior_passable_cells += 1
        
        if interior_passable_cells == 0:
            return 0.0
        
        # Convert remaining coverage to percentage of interior passable cells
        remaining_cells = remaining_coverage * total_cells
        safe_percentage = min(0.3, remaining_cells / interior_passable_cells)
        
        return max(0.0, safe_percentage)
    
    def is_terrain_connected(self) -> bool:
        """Validates that all passable terrain (0) is reachable using flood fill"""
        # Find all passable cells
        passable_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.is_passable(self.terrain[y][x]):
                    passable_cells.append((x, y))
        
        if not passable_cells:
            return True  # No passable cells, trivially connected
        
        # Start flood fill from the first passable cell
        start_x, start_y = passable_cells[0]
        visited = set()
        queue = deque([(start_x, start_y)])
        visited.add((start_x, start_y))
        
        # Directions: North, East, South, West
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        while queue:
            x, y = queue.popleft()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Check bounds and if cell is passable and not visited
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    self.is_passable(self.terrain[ny][nx]) and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        # Check if all passable cells were reached
        return len(visited) == len(passable_cells)

    def create_obstacles(self, room, obstacle_percentage: float = 0.3) -> None:
        """Creates random obstacles while ensuring all passable terrain remains reachable"""
        
        # Don't modify edge terrain - only work with interior cells
        interior_cells = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.is_passable(self.terrain[y][x]):  # Only consider passable interior cells
                    interior_cells.append((x, y))
        
        if not interior_cells:
            return  # No interior cells to modify
        
        # Randomly shuffle the interior cells
        random.shuffle(interior_cells)
        
        # Try to place obstacles on a percentage of interior passable cells
        max_obstacles = int(len(interior_cells) * obstacle_percentage)
        
        obstacles_placed = 0
        for x, y in interior_cells:
            if obstacles_placed >= max_obstacles:
                break
                
            # Temporarily place obstacle
            self.terrain[y][x] = Location.FOREST
            
            # Check if terrain is still connected
            if self.is_terrain_connected():
                obstacles_placed += 1
            else:
                # Remove obstacle if it breaks connectivity
                self.terrain[y][x] = Location.GRASS

    def expand_terrain_pools(self) -> None:
        """Expands water and mountain terrain from edges toward center in 2x2 pools"""
        # Find water and mountain terrain on edges
        edge_terrain_positions = []
        
        # Check top and bottom edges
        for x in range(self.width):
            if self.terrain[0][x] in [Location.WATER, Location.MOUNTAIN]:
                edge_terrain_positions.append((x, 0, self.terrain[0][x]))
            if self.terrain[self.height-1][x] in [Location.WATER, Location.MOUNTAIN]:
                edge_terrain_positions.append((x, self.height-1, self.terrain[self.height-1][x]))
        
        # Check left and right edges
        for y in range(self.height):
            if self.terrain[y][0] in [Location.WATER, Location.MOUNTAIN]:
                edge_terrain_positions.append((0, y, self.terrain[y][0]))
            if self.terrain[y][self.width-1] in [Location.WATER, Location.MOUNTAIN]:
                edge_terrain_positions.append((self.width-1, y, self.terrain[y][self.width-1]))
        
        random.shuffle(edge_terrain_positions)

        # For each water/mountain terrain found on edges, try to expand inward
        for edge_x, edge_y, terrain_type in edge_terrain_positions:
            self.expand_from_edge(edge_x, edge_y, terrain_type)

    def expand_from_edge(self, start_x: int, start_y: int, terrain_type: int,
                         min_expansions: int = 0, max_expansions: int = 4) -> None:
        """Expands a specific terrain type from an edge position toward center"""
        max_expansions = random.randint(min_expansions, max_expansions)
        max_steps = 8
        expansions_made = 0
        step = 0
        current_x, current_y = start_x, start_y

        while expansions_made < max_expansions and step < max_steps:
            random_value = random.random()
            if random_value > 0.75:
                random_offset_x = 1
                random_offset_y = 0
            elif random_value > 0.5:
                random_offset_x = -1
                random_offset_y = 0
            elif random_value > 0.25:
                random_offset_x = 0
                random_offset_y = 1
            else:
                random_offset_x = 0
                random_offset_y = -1
            
            pool_x = current_x + random_offset_x
            pool_y = current_y + random_offset_y
            pool_coords = [(pool_x, pool_y), (pool_x+1, pool_y), (pool_x, pool_y+1), (pool_x+1, pool_y+1)]

            if self.try_place_terrain_pool(pool_coords, terrain_type):
                expansions_made += 1
                current_x, current_y = pool_x, pool_y
            step += 1

    def try_place_terrain_pool(self, pool_coords: list[tuple[int, int]], terrain_type: int) -> bool:
        """Attempts to place a 2x2 pool of terrain. Returns True if successful."""
        identical_terrain_count = 0
        original_terrain = []
        
        for x, y in pool_coords:
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return False
            
            current_terrain = self.terrain[y][x]
            original_terrain.append((x, y, current_terrain))
            is_edge = (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1)
            
            if is_edge and current_terrain != terrain_type:
                return False
            
            if current_terrain == terrain_type:
                identical_terrain_count += 1
            elif self.is_passable(current_terrain) == False:
                return False
        
        if identical_terrain_count == 2 or identical_terrain_count == 3:
            # Temporarily place the terrain pool
            for x, y in pool_coords:
                self.terrain[y][x] = terrain_type
            
            # Check if terrain is still connected
            if self.is_terrain_connected():
                return True  # Pool successfully placed
            else:
                # Rollback - restore original terrain
                for x, y, original in original_terrain:
                    self.terrain[y][x] = original
                return False
        else:
            return False

    def get_layout(self) -> str:
        layout = ""
        for y in range(self.height):
            for x in range(self.width):
                if self.terrain[y][x] == Location.FOREST:
                    layout += "$ "
                elif self.terrain[y][x] == Location.ROAD:
                    layout += "  "
                elif self.terrain[y][x] == Location.GRASS:
                    layout += ", "
                elif self.terrain[y][x] == Location.MOUNTAIN:
                    layout += "# "
                elif self.terrain[y][x] == Location.WATER:
                    layout += "~ "
                elif self.terrain[y][x] == Location.FENCE:
                    layout += "= "

            layout += "\n"
        return layout
    
    def create_fences(self) -> None:
        """Creates fence terrain that extends in straight lines"""
        # Random number of fence starting points (1-3)
        num_fences = random.randint(1, 3)
        
        for _ in range(num_fences):
            # Find a random interior passable location for fence start
            interior_cells = []
            for y in range(2, self.height - 2):
                for x in range(2, self.width - 2):
                    if self.is_passable(self.terrain[y][x]):
                        interior_cells.append((x, y))
            
            if not interior_cells:
                continue
                
            start_x, start_y = random.choice(interior_cells)
            
            # Choose direction: 0=horizontal, 1=vertical
            direction = random.randint(0, 1)
            
            # Create the fence
            fence_cells = self.extend_fence(start_x, start_y, direction)
            
            # Check if fence breaks connectivity
            if not self.is_terrain_connected():
                # Punch a hole in the fence to restore connectivity
                self.punch_fence_hole(fence_cells)
    
    def extend_fence(self, start_x: int, start_y: int, direction: int) -> list[tuple[int, int]]:
        """Extends a fence from starting position until obstacles are reached"""
        fence_cells = []
        
        if direction == 0:  # Horizontal fence
            # Extend left
            x = start_x
            while x >= 1 and self.is_passable(self.terrain[start_y][x]):
                fence_cells.append((x, start_y))
                self.terrain[start_y][x] = Location.FENCE
                x -= 1
            
            # Extend right
            x = start_x + 1
            while x < self.width - 1 and self.is_passable(self.terrain[start_y][x]):
                fence_cells.append((x, start_y))
                self.terrain[start_y][x] = Location.FENCE
                x += 1
                
        else:  # Vertical fence
            # Extend up
            y = start_y
            while y >= 1 and self.is_passable(self.terrain[y][start_x]):
                fence_cells.append((start_x, y))
                self.terrain[y][start_x] = Location.FENCE
                y -= 1
            
            # Extend down
            y = start_y + 1
            while y < self.height - 1 and self.is_passable(self.terrain[y][start_x]):
                fence_cells.append((start_x, y))
                self.terrain[y][start_x] = Location.FENCE
                y += 1
        
        return fence_cells
    
    def punch_fence_hole(self, fence_cells: list[tuple[int, int]]) -> None:
        """Punches a random hole in the fence to restore connectivity"""
        if not fence_cells:
            return
            
        # Try multiple random positions until connectivity is restored
        max_attempts = min(10, len(fence_cells))
        attempts = 0
        
        # Shuffle fence cells to try random positions
        fence_positions = fence_cells.copy()
        random.shuffle(fence_positions)
        
        for x, y in fence_positions:
            if attempts >= max_attempts:
                break
                
            # Temporarily remove fence piece
            self.terrain[y][x] = Location.GRASS
            
            # Check if connectivity is restored
            if self.is_terrain_connected():
                return  # Hole successfully punched
            else:
                # Restore fence piece and try next position
                self.terrain[y][x] = Location.FENCE
                attempts += 1
        
        # If no single hole works, remove the fence altogether
        for x, y in fence_cells:
            self.terrain[y][x] = Location.GRASS
    