import random
from collections import deque
from math import floor

class Location():
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    # Terrain types
    BRIDGE_H = -3
    BRIDGE_V = -2
    ROAD = -1
    GRASS = 0
    FOREST = 1
    FENCE = 2
    WATER = 9
    MOUNTAIN = 18

    """Describes a location in the maze"""
    def __init__(self, room, width: int = 15, height: int = 15, gap: int = 3,
                 base_tile: int = 0, base_inaccessible_tile: int = None,
                 mountain_chance: float = 0.3, fence_chance: float = 0.3, 
                 min_obstacle_coverage: float = 0.1, max_obstacle_coverage: float = 0.5):
        if base_inaccessible_tile:
            self.inaccessible_terrain = True
            self.terrain = [[base_inaccessible_tile for x in range(width)] for y in range(height)]
        else:
            self.inaccessible_terrain = False
            self.terrain = [[base_tile for x in range(width)] for y in range(height)]
        self.width = width
        self.height = height
        self.create_edges(room, gap)
        
        if self.inaccessible_terrain:
            if room.paths[Location.NORTH] == 1:
                # self.create_bridge((self.width - 1) // 2, 1, Location.SOUTH)
                self.erase_pool((self.width - 1) // 2, 0, Location.ROAD, Location.WATER)
            if room.paths[Location.SOUTH] == 1:
                # self.create_bridge((self.width - 1) // 2, self.height - 2, Location.NORTH)
                self.erase_pool((self.width - 1) // 2, self.height - 1, Location.ROAD, Location.WATER)
            if room.paths[Location.WEST] == 1:
                # self.create_bridge(1, (self.height - 1) // 2, Location.EAST)
                self.erase_pool(0, (self.height - 1) // 2, Location.ROAD, Location.WATER)
            if room.paths[Location.EAST] == 1:
                # self.create_bridge(self.width - 2, (self.height - 1) // 2, Location.WEST)
                self.erase_pool(self.width - 1, (self.height - 1) // 2, Location.ROAD, Location.WATER)
            
            x = (self.width - 1) // 2
            y = (self.width - 1) // 2
            
            if self.try_erase_terrain_pool([(x, y), (x+1, y), (x, y+1), (x+1, y+1)], Location.ROAD, Location.WATER):
                north_bridge = self.check_bridge_viability(x, y, Location.NORTH)
                east_bridge = self.check_bridge_viability(x + 1, y, Location.EAST)

                if north_bridge[0]:
                    self.create_bridge(x, y - 1, Location.NORTH, north_bridge[1])
                if east_bridge[0]:
                    self.create_bridge(x + 2, y, Location.EAST, east_bridge[1])

        # Random check to add mountain terrain near center
        if random.random() < mountain_chance:
            self.add_center_mountains()
        
        self.expand_edge_pools(ignore_passability=self.inaccessible_terrain)
        
        # Create some trees which the fences can collide with
        # But not so many, that'd make the fences too short
        if random.random() < fence_chance:
            self.create_obstacles(room, 0.1)
            self.create_fences()
        
        obstacle_coverage = random.uniform(min_obstacle_coverage, max_obstacle_coverage)
        self.create_obstacles(room, obstacle_coverage)
        self.rotate_all_obstacles()
    
    def get_terrain(self, x: int, y: int) -> int:
        return self.terrain[y][x]
    
    def get_passable(self, x: int, y: int) -> bool:
        return self.terrain[y][x] <= 0
    
    def get_terrain_type(self, x: int, y: int) -> int:
        return self.get_obstacle_type(self.terrain[y][x])
    
    def _get_obstacle(self, type: int) -> int:
        """Returns the obstacle. If None, returns a random, valid obstacle."""
        if type is None:
            # TODO I should create a list of valid obstacles
            return Location.FOREST
        else:
            return type

    def create_edges(self, room, gap: int) -> None:
        """Creates edges around the room"""
        for x in range(self.width // 2):
            self.terrain[0][x] = self._get_obstacle(room.terrain[Location.WEST])
            self.terrain[self.height - 1][x] = self._get_obstacle(room.terrain[Location.SOUTH])
        for y in range(self.height // 2):
            self.terrain[y][0] = self._get_obstacle(room.terrain[Location.WEST])
            self.terrain[y][self.width - 1] = self._get_obstacle(room.terrain[Location.NORTH])
        for x in range(self.width // 2, self.width):
            self.terrain[0][x] = self._get_obstacle(room.terrain[Location.NORTH])
            self.terrain[self.height - 1][x] = self._get_obstacle(room.terrain[Location.EAST])
        for y in range(self.height // 2, self.height):
            self.terrain[y][0] = self._get_obstacle(room.terrain[Location.SOUTH])
            self.terrain[y][self.width - 1] = self._get_obstacle(room.terrain[Location.EAST])
        
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

    def expand_edge_pools(self, ignore_passability: bool = False) -> None:
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
            self.expand_pool(edge_x, edge_y, terrain_type, ignore_passability=ignore_passability)

    def expand_pool(self, start_x: int, start_y: int, terrain_type: int,
                    min_expansions: int = 1, max_expansions: int = 4,
                    ignore_passability: bool = False) -> None:
        """Expands a specific pool of terrain type"""
        max_expansions = max(random.randint(min_expansions, max_expansions), 1)
        max_steps = max_expansions * 2
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
            
            pool_x = max(0, min(self.width - 2, current_x + random_offset_x))
            pool_y = max(0, min(self.height - 2, current_y + random_offset_y))
            pool_coords = [(pool_x, pool_y), (pool_x+1, pool_y), (pool_x, pool_y+1), (pool_x+1, pool_y+1)]

            if self.try_place_terrain_pool(pool_coords, terrain_type, ignore_passability=ignore_passability):
                expansions_made += 1
                current_x, current_y = pool_x, pool_y
            step += 1

    def try_place_terrain_pool(self, pool_coords: list[tuple[int, int]], terrain_type: int,
                               ignore_passability: bool = False) -> bool:
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
            elif current_terrain == terrain_type:
                identical_terrain_count += 1
            elif current_terrain == Location.BRIDGE_H or current_terrain == Location.BRIDGE_V:
                return False
        
        if identical_terrain_count == 2 or identical_terrain_count == 3:
            # Temporarily place the terrain pool
            for x, y in pool_coords:
                self.terrain[y][x] = terrain_type
            
            # Check if terrain is still connected
            if ignore_passability or self.is_terrain_connected():
                return True  # Pool successfully placed
            else:
                # Rollback - restore original terrain
                for x, y, original in original_terrain:
                    self.terrain[y][x] = original
                return False
        else:
            return False
    
    def erase_pool(self, start_x: int, start_y: int, terrain_type: int,
                    erased_terrain_type: int, 
                    min_expansions: int = 1, max_expansions: int = 4) -> None:
        """Expands a specific terrain type, erasing existing pool terrain"""
        max_expansions = max(random.randint(min_expansions, max_expansions), 1)
        max_steps = max_expansions * 2
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
            
            pool_x = max(0, min(self.width - 2, current_x + random_offset_x))
            pool_y = max(0, min(self.height - 2, current_y + random_offset_y))
            pool_coords = [(pool_x, pool_y), (pool_x+1, pool_y), (pool_x, pool_y+1), (pool_x+1, pool_y+1)]

            if self.try_erase_terrain_pool(pool_coords, terrain_type, erased_terrain_type):
                expansions_made += 1
                current_x, current_y = pool_x, pool_y
            step += 1
    
    def validate_pool(self, x: int, y: int) -> bool:
        """Checks if a tile belongs to a valid pool.
        A pool is valid if it's constructed out of 2x2 shapes of the same terrain type.
        Out of bounds cells are assumed to be of the same terrain type."""
        terrain_type = self.get_terrain_type(x, y)
        coordinates = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
        diff = [(0, 0), (-1, 0), (0, -1), (-1, -1)]

        for dx, dy in diff:
            success = True
            for x, y in coordinates:
                try:
                    if self.get_terrain_type(x + dx, y + dy) != terrain_type:
                        success = False
                        break
                except IndexError:
                    pass
            if success:
                return True
        return False

    def try_erase_terrain_pool(self, pool_coords: list[tuple[int, int]], terrain_type: int,
                               erased_terrain_type: int) -> bool:
        """Attempts to places accessible terrain in a 2x2 pool.
        This may erase existing pool terrain.
        Ensures the erasure of terrain don't break pool terrain rules.
        """
        min_x = pool_coords[0][0]
        min_y = pool_coords[0][1]
        # success = True
        existing_terrain = []
        
        for x, y in pool_coords:
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return False
            elif self.get_terrain(x, y) not in (erased_terrain_type, terrain_type):
                return False
            existing_terrain.append((x, y, self.get_terrain(x, y)))
            self.terrain[y][x] = terrain_type
        
        # Construct a list of tuples
        # The first coordinate pair form a frame 6x6 around the pool
        # The second coordinate pair form a frame 4x4 around the pool
        # What we're interested in is if there's pool terrain in the 4x4 frame
        # which doesn't extend outwards into the 6x6 frame.
        # That would be an isolated 1x1 pool, which is a rule violation.
        # frame = []
        
        # for x in range(min_x - 1, min_x + 3):
        #     frame.append((x, min_y - 2, x, min_y - 1))
        #     frame.append((x, min_y + 3, x, min_y + 2))
        
        # for y in range(min_y - 1, min_y + 3):
        #     frame.append((min_x - 2, y, min_x - 1, y))
        #     frame.append((min_x + 3, y, min_x + 2, y))
        
        # frame.append((min_x - 2, min_y - 2, min_x - 1, min_y - 1))
        # frame.append((min_x + 3, min_y - 2, min_x + 2, min_y - 1))
        # frame.append((min_x - 2, min_y + 3, min_x - 1, min_y + 2))
        # frame.append((min_x + 3, min_y + 3, min_x + 2, min_y + 2))

        # for x_out, y_out, x_in, y_in in frame:
        #     try:
        #         if self.terrain[y_in][x_in] == erased_terrain_type \
        #         and self.terrain[y_out][x_out] != erased_terrain_type:
        #             success = False
        #             break
        #     except IndexError:
        #         pass
        
        # Let's just use the validate_pool function instead.
        # I'm not sure if my current solution works and it looks complex.
        # I'll still need a frame...
        frame = []
        for x in range(min_x - 1, min_x + 3):
            frame.append((x, min_y - 1))
            frame.append((x, min_y + 2))
        
        for y in range(min_y, min_y + 2):
            frame.append((min_x - 1, y))
            frame.append((min_x + 2, y))
        
        for x, y in frame:
            try:
                if self.get_terrain_type(x, y) == erased_terrain_type and self.validate_pool(x, y) == False:
                    for x, y, original in existing_terrain:
                        self.terrain[y][x] = original
                    return False
            except IndexError:
                pass
        return True
        
        # if not success:
        #     for x, y, original in existing_terrain:
        #         self.terrain[y][x] = original
        # return success

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
                elif self.get_obstacle_type(self.terrain[y][x]) == Location.MOUNTAIN:
                    layout += "# "
                elif self.get_obstacle_type(self.terrain[y][x]) == Location.WATER:
                    layout += "~ "
                elif self.terrain[y][x] == Location.FENCE or self.terrain[y][x] == Location.BRIDGE_H:
                    layout += "= "
                elif self.terrain[y][x] == Location.BRIDGE_V:
                    layout += "| "

            layout += "\n"
        return layout
    
    def get_raw_layout(self) -> str:
        layout = ""
        for y in range(self.height):
            for x in range(self.width):
                layout += f"{self.terrain[y][x]:02d} "
            layout += "\n"
        return layout
    
    def create_fences(self, min_fences: int = 1, max_fences: int = 3) -> None:
        """Creates fence terrain that extends in straight lines"""
        num_fences = random.randint(min_fences, max_fences)
        
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
    
    def get_obstacle_type(self, obstacle: int) -> int:
        """Returns the type of obstacle.
        The type is the same for all rotations."""
        if obstacle >= Location.WATER:
            obstacle_type = obstacle - obstacle % 9
        else:
            obstacle_type = obstacle
        return obstacle_type
    
    def rotate_obstacle(self, x: int, y: int) -> None:
        """Replaces the obstacle with a rotated version,
        depending on how the obstacle borders to other types of terrain.
        Only works for obstacles that are placed in 2x2 pools.
        Assumes the obstacle has no more than 2 borders to other types of terrain."""
        obstacle = self.get_terrain(x, y)
        directions = ((0, -1), (1, 0), (0, 1), (-1, 0))
        surroundings = [None, None, None, None]

        for i, (dx, dy) in enumerate(directions):
            try:
                surroundings[i] = self.get_obstacle_type(self.get_terrain(x + dx, y + dy))
            except IndexError:
                surroundings[i] = obstacle
        
        # Check for north, consider northeast and northwest
        if obstacle != surroundings[0]:
            if obstacle != surroundings[1]:
                self.terrain[y][x] = obstacle + 2
            elif obstacle != surroundings[3]:
                self.terrain[y][x] = obstacle + 8
            else:
                self.terrain[y][x] = obstacle + 1
        # Otherwise, check for south
        elif obstacle != surroundings[2]:
            if obstacle != surroundings[1]:
                self.terrain[y][x] = obstacle + 4
            elif obstacle != surroundings[3]:
                self.terrain[y][x] = obstacle + 6
            else:
                self.terrain[y][x] = obstacle + 5
        # Otherwise, check for east
        elif obstacle != surroundings[1]:
            self.terrain[y][x] = obstacle + 3
        # Finally, check for west
        elif obstacle != surroundings[3]:
            self.terrain[y][x] = obstacle + 7
        
        # I guess that's it. There's a lot of if-statements,
        # so there might be a better way to do it.
        # Yeah, that works for now.
        # But there's actually even more variants I need to consider.
        # For instance, an obstacle with free space to the northwest,
        # it's going to need a northwest slope.
        # Except no free space should shine through,
        # so it's not a regular northwest slope.
        # Based on my algorithm, I should only need 4 of these special shapes.
        # A tile cannot have free space in two diagonal directions.

    def rotate_all_obstacles(self) -> None:
        """Rotates all obstacles in the location."""
        for y in range(self.height):
            for x in range(self.width):
                # if self.get_terrain(x, y) >= Location.WATER:
                # Water should be rotated but I don't have the images yet
                if self.get_terrain(x, y) >= Location.MOUNTAIN:
                    self.rotate_obstacle(x, y)

    def create_bridge(self, start_x: int, start_y: int, direction: int, length: int = None) -> list[tuple[int, int]]:
        """Extends a bridge from starting position in a straight line.
        Bridge is 2 spaces wide and extends for random length.
        Direction: Location.NORTH, Location.EAST, Location.SOUTH, or Location.WEST
        """
        bridge_cells = []
        
        # Determine random length if not specified
        if length is None:
            length = random.randint(3, 13)
        
        if direction == Location.EAST or direction == Location.WEST:
            # Horizontal bridge (extends east-west, 2 spaces wide north-south)
            bridge_type = Location.BRIDGE_H
            
            # Center the bridge vertically around start_y (2 spaces wide)
            start_bridge_y = max(0, min(self.height - 2, start_y))
            
            if direction == Location.EAST:
                # Extend eastward
                for x in range(start_x, min(start_x + length, self.width)):
                    for y in range(start_bridge_y, start_bridge_y + 2):
                        if 0 <= y < self.height:
                            bridge_cells.append((x, y))
                            self.terrain[y][x] = bridge_type
            else:  # WEST
                # Extend westward
                for x in range(max(0, start_x - length + 1), start_x + 1):
                    for y in range(start_bridge_y, start_bridge_y + 2):
                        if 0 <= y < self.height:
                            bridge_cells.append((x, y))
                            self.terrain[y][x] = bridge_type
                            
        elif direction == Location.NORTH or direction == Location.SOUTH:
            # Vertical bridge (extends north-south, 2 spaces wide east-west)
            bridge_type = Location.BRIDGE_V
            
            # Center the bridge horizontally around start_x (2 spaces wide)
            start_bridge_x = max(0, min(self.width - 2, start_x))
            
            if direction == Location.SOUTH:
                # Extend southward
                for y in range(start_y, min(start_y + length, self.height)):
                    for x in range(start_bridge_x, start_bridge_x + 2):
                        if 0 <= x < self.width:
                            bridge_cells.append((x, y))
                            self.terrain[y][x] = bridge_type
            else:  # NORTH
                # Extend northward
                for y in range(max(0, start_y - length + 1), start_y + 1):
                    for x in range(start_bridge_x, start_bridge_x + 2):
                        if 0 <= x < self.width:
                            bridge_cells.append((x, y))
                            self.terrain[y][x] = bridge_type
        
        return bridge_cells

    def check_bridge_viability(self, start_x: int, start_y: int, direction: int, max_search_distance: int = 15) -> tuple[bool, int]:
        """Checks if bridge construction is viable from a 2x2 starting point.
        
        Searches in a straight line for passable terrain in the specified direction.
        Performs 2 parallel searches (for 2-cell wide bridge) and both must find 
        passable terrain at roughly the same distance.
        
        Args:
            start_x: X coordinate of top-left corner of 2x2 starting area
            start_y: Y coordinate of top-left corner of 2x2 starting area  
            direction: Direction to search (Location.NORTH, EAST, SOUTH, WEST)
            max_search_distance: Maximum distance to search
            
        Returns:
            tuple: (is_viable, bridge_length) where bridge_length is the distance
                   to passable terrain, or 0 if not viable
        """
        
        # Define the two search starting points based on direction
        if direction == Location.EAST or direction == Location.WEST:
            # Horizontal bridge - search from top and bottom of 2x2 area
            search_points = [(start_x, start_y), (start_x, start_y + 1)]
            step_x = 1 if direction == Location.EAST else -1
            step_y = 0
        elif direction == Location.NORTH or direction == Location.SOUTH:
            # Vertical bridge - search from left and right of 2x2 area  
            search_points = [(start_x, start_y), (start_x + 1, start_y)]
            step_x = 0
            step_y = 1 if direction == Location.SOUTH else -1
        else:
            return False, 0
        
        # Search distances for each parallel line
        distances = []
        
        for search_x, search_y in search_points:
            distance = 0
            current_x, current_y = search_x, search_y
            
            # Search in the specified direction
            for step in range(1, max_search_distance + 1):
                current_x += step_x
                current_y += step_y
                
                # Check bounds
                if current_x < 0 or current_x >= self.width or current_y < 0 or current_y >= self.height:
                    distance = -1  # Hit boundary without finding passable terrain
                    break
                
                # Check if we found passable terrain
                if self.is_passable(self.terrain[current_y][current_x]):
                    distance = step
                    break
            
            distances.append(distance)
        
        # Check if both searches were successful
        if -1 in distances:
            return False, 0  # At least one search hit a boundary
        
        # Check if both found passable terrain at roughly the same distance
        # Allow a difference of 1 cell
        distance_diff = abs(distances[0] - distances[1])
        if distance_diff <= 1:
            # Return the shorter distance (conservative estimate)
            bridge_length = min(distances)
            return True, bridge_length
        else:
            return False, 0