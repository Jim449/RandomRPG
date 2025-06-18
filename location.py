import random
from collections import deque

class Location():
    """Describes a location in the maze.
    A location occupies a single screen."""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    # Expansion types
    EXPAND_POOL = 0
    EXPAND_LINE = 1
    EXPAND_BRIDGE = 2
    SINGLE_TILE = 3
    REGULAR_PASSABLE = 4
    # Terrain types
    BRIDGE_H = -27
    BRIDGE_V = -18
    BRIDGE = -2
    ROAD = -1
    GRASS = 0
    FOREST = 1
    FENCE = 2
    WATER = 9
    MOUNTAIN = 18

    def __init__(self, room, allowed_obstacles: tuple[int], width: int = 15, height: int = 15, gap: int = 3,
                 base_tile: int = 0, base_inaccessible_tile: int = None,
                 pool_terrain_chance: float = 0.3, pool_terrain_growth: tuple[int, int] = (0, 2),
                 line_terrain_chance: float = 0.3, line_terrain_amount: tuple[int, int] = (1, 3),
                 obstacle_coverage: tuple[float, float] = (0.2, 0.4)):
        """Creates a new location.
        
        Args:
            room: The room that the location belongs to.
            allowed_obstacles: A tuple of allowed obstacles. Excludes large corner obstacles.
            width: The width of the location.
            height: The height of the location.
            gap: The size of the entrance.
            base_tile: The base tile of the location.
            base_inaccessible_tile: A non-passable tile which will be placed across the entire location at creation start.
            pool_terrain_chance: The chance of a pool terrain being placed.
            pool_terrain_growth: The minimum and maximum number of expansions for a pool terrain. Applies to both large corner terrain and interior terrain.
            line_terrain_chance: The chance of a line terrain being placed.
            line_terrain_amount: The minimum and maximum number of line terrain being placed.
            obstacle_coverage: The minimum and maximum percentage of the location that can be occupied by single tile obstacles.
        """
        self.width = width
        self.height = height
        self.gap = gap
        self.room = room
        self.base_tile = base_tile
        self.base_inaccessible_tile = base_inaccessible_tile
        self.min_obstacle_coverage = obstacle_coverage[0]
        self.max_obstacle_coverage = obstacle_coverage[1]
        self.pool_terrain_chance = pool_terrain_chance
        self.pool_terrain_growth = pool_terrain_growth
        self.line_terrain_chance = line_terrain_chance
        self.line_terrain_amount = line_terrain_amount
        self.pool_terrain_allowed = []
        self.line_terrain_allowed = []
        self.single_tile_terrain_allowed = []

        for terrain in allowed_obstacles:
            expansion_type = self.get_terrain_expansion_type(terrain)
            if expansion_type == Location.EXPAND_POOL:
                self.pool_terrain_allowed.append(terrain)
            elif expansion_type == Location.EXPAND_LINE:
                self.line_terrain_allowed.append(terrain)
            elif expansion_type == Location.SINGLE_TILE:
                self.single_tile_terrain_allowed.append(terrain)

        if base_inaccessible_tile:
            self.inaccessible_terrain = True
            self.create_lake_location()
        else:
            self.inaccessible_terrain = False
            self.create_regular_location()
    
    def get_terrain(self, x: int, y: int) -> int:
        """Returns the terrain at the given coordinates"""
        return self.terrain[y][x]
    
    def get_passable(self, x: int, y: int) -> bool:
        """Returns True if the terrain at the given coordinates is passable"""
        return self.terrain[y][x] <= 0
    
    def get_terrain_type_at(self, x: int, y: int) -> int:
        """Returns the type of terrain at the given coordinates,
        disregarding the rotation of the terrain"""
        return self.get_terrain_type(self.terrain[y][x])
    
    def get_terrain_type(self, terrain: int) -> int:
        """Returns the type of terrain.
        The type is the same for all rotations."""
        if terrain >= Location.WATER:
            terrain_type = terrain - terrain % 9
        elif terrain >= Location.BRIDGE_H and terrain <= Location.BRIDGE_H + 8:
            terrain_type = Location.BRIDGE_H
        elif terrain >= Location.BRIDGE_V and terrain <= Location.BRIDGE_V + 8:
            terrain_type = Location.BRIDGE_V
        else:
            terrain_type = terrain
        return terrain_type
    
    def get_terrain_expansion_type(self, terrain: int) -> int:
        """Returns the expansion type of the terrain.
        This determines how the terrain is placed
        and how existing terrain can be expanded."""
        terrain_type = self.get_terrain_type(terrain)
        if terrain_type == Location.MOUNTAIN:
            return Location.EXPAND_POOL
        elif terrain_type == Location.WATER:
            return Location.EXPAND_POOL
        elif terrain_type == Location.BRIDGE_H:
            return Location.EXPAND_BRIDGE
        elif terrain_type == Location.BRIDGE_V:
            return Location.EXPAND_BRIDGE
        elif terrain_type == Location.FENCE:
            return Location.EXPAND_LINE
        elif terrain in (Location.ROAD, Location.GRASS):
            return Location.REGULAR_PASSABLE
        else:
            return Location.SINGLE_TILE
    
    def get_coordinates_box(self, x: int, y: int) -> list[tuple[int, int]]:
        """Returns a 2x2 box of coordinates, with (x, y) at the top left corner.
        Coordinates are returned in clockwise order, starting from the top left."""
        return [(x, y), (x+1, y), (x+1, y+1), (x, y+1)]
    
    def get_box_border(self, box: list[tuple[int, int]]) -> list[int]:
        """Returns the coordinates of the border of the box
        in order of north, east, south, west"""
        min_x = 100
        max_x = 0
        min_y = 100
        max_y = 0
        
        for x, y in box:
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
        
        return [min_y, max_x, max_y, min_x]

    def get_obstacle(self, available_obstacles: list[int], type: int = None) -> int:
        """Returns the obstacle. If None, returns a random, valid obstacle."""
        if type is None:
            return random.choice(available_obstacles)
        else:
            return type

    def create_edges(self, room, gap: int) -> None:
        """Creates edges around the room"""
        for x in range(self.width // 2):
            self.terrain[0][x] = self.get_obstacle(self.single_tile_terrain_allowed, room.terrain[Location.WEST])
            self.terrain[self.height - 1][x] = self.get_obstacle(self.single_tile_terrain_allowed, room.terrain[Location.SOUTH])
        for y in range(self.height // 2):
            self.terrain[y][0] = self.get_obstacle(self.single_tile_terrain_allowed, room.terrain[Location.WEST])
            self.terrain[y][self.width - 1] = self.get_obstacle(self.single_tile_terrain_allowed, room.terrain[Location.NORTH])
        for x in range(self.width // 2, self.width):
            self.terrain[0][x] = self.get_obstacle(self.single_tile_terrain_allowed, room.terrain[Location.NORTH])
            self.terrain[self.height - 1][x] = self.get_obstacle(self.single_tile_terrain_allowed, room.terrain[Location.EAST])
        for y in range(self.height // 2, self.height):
            self.terrain[y][0] = self.get_obstacle(self.single_tile_terrain_allowed, room.terrain[Location.SOUTH])
            self.terrain[y][self.width - 1] = self.get_obstacle(self.single_tile_terrain_allowed, room.terrain[Location.EAST])
        
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
    
    def add_pool_terrain(self, terrain_type: int, min_expansions: int = 0, max_expansions: int = 8) -> None:
        """Adds pool terrain to a random position"""
        terrain_x = random.randint(1, self.width - 3)
        terrain_y = random.randint(1, self.height - 3)
        
        terrain_coords = [
            (terrain_x, terrain_y),
            (terrain_x + 1, terrain_y),
            (terrain_x, terrain_y + 1),
            (terrain_x + 1, terrain_y + 1)
        ]
        
        can_place = True
        for x, y in terrain_coords:
            if not self.is_passable(self.terrain[y][x]):
                can_place = False
                break
        
        if can_place:
            for x, y in terrain_coords:
                self.terrain[y][x] = terrain_type
            self.expand_pool(terrain_x, terrain_y, terrain_type,
                             min_expansions=min_expansions, max_expansions=max_expansions)
    
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

    def create_obstacles(self, obstacle_percentage: float = 0.3) -> None:
        """Creates random obstacles while ensuring all passable terrain remains reachable"""
        
        interior_cells = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Checks for passable terrain that is not a bridge
                if self.get_terrain_expansion_type(self.terrain[y][x]) == Location.REGULAR_PASSABLE:
                    interior_cells.append((x, y))
        
        if not interior_cells:
            return
        
        random.shuffle(interior_cells)
        max_obstacles = int(len(interior_cells) * obstacle_percentage)
        
        obstacles_placed = 0
        for x, y in interior_cells:
            if obstacles_placed >= max_obstacles:
                break
            
            terrain_type = self.get_obstacle(self.single_tile_terrain_allowed, None)
            self.terrain[y][x] = terrain_type
            
            if self.is_terrain_connected():
                obstacles_placed += 1
            else:
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
            pool_coords = self.get_coordinates_box(pool_x, pool_y)

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
                    min_expansions: int = 1, max_expansions: int = 4,
                    avoid_bridges: bool = False) -> None:
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
            pool_coords = self.get_coordinates_box(pool_x, pool_y)

            if self.try_erase_terrain_pool(pool_coords, terrain_type, erased_terrain_type,
                                           avoid_bridges=avoid_bridges):
                expansions_made += 1
                current_x, current_y = pool_x, pool_y
            step += 1
    
    def validate_pool(self, x: int, y: int) -> bool:
        """Checks if a tile belongs to a valid pool.
        A pool is valid if it's constructed out of 2x2 shapes of the same terrain type.
        Out of bounds cells are assumed to be of the same terrain type."""
        terrain_type = self.get_terrain_type_at(x, y)
        coordinates = self.get_coordinates_box(x, y)
        diff = [(0, 0), (-1, 0), (0, -1), (-1, -1)]

        for dx, dy in diff:
            success = True
            for x, y in coordinates:
                try:
                    if self.get_terrain_type_at(x + dx, y + dy) != terrain_type:
                        success = False
                        break
                except IndexError:
                    pass
            if success:
                return True
        return False

    def try_erase_terrain_pool(self, pool_coords: list[tuple[int, int]], terrain_type: int,
                               erased_terrain_type: int, check_only: bool = False,
                               avoid_bridges: bool = False) -> bool:
        """Attempts to places accessible terrain in a 2x2 pool.
        This may erase existing pool terrain.
        Ensures the erasure of terrain doesn't break pool terrain rules.
        Returns True if the erasure is successful or possible.
        If check_only is True, the terrain is not actually erased.
        If avoid bridges is True, water must be preserved around bridges.
        """
        min_x = pool_coords[0][0]
        min_y = pool_coords[0][1]
        success = True
        existing_terrain = []
        
        for x, y in pool_coords:
            is_edge = (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1)
            
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return False
            elif self.get_terrain_type_at(x, y) not in (erased_terrain_type, terrain_type):
                return False
            elif is_edge and self.get_terrain_type_at(x, y) != terrain_type:
                return False
            existing_terrain.append((x, y, self.get_terrain(x, y)))

            if check_only == False:
                self.terrain[y][x] = terrain_type
        
        frame = []
        for x in range(min_x, min_x + 2):
            frame.append((x, min_y - 1))
            frame.append((x, min_y + 2))
        
        for y in range(min_y, min_y + 2):
            frame.append((min_x - 1, y))
            frame.append((min_x + 2, y))
        
        for x, y in frame:
            try:
                if avoid_bridges and self.get_terrain_type_at(x, y) in (Location.BRIDGE_H, Location.BRIDGE_V):
                    success = False
                elif self.get_terrain_type_at(x, y) == erased_terrain_type and self.validate_pool(x, y) == False:
                    success = False
            except IndexError:
                pass
        
        if success == False:
            if check_only == False:
                for x, y, original in existing_terrain:
                    self.terrain[y][x] = original
        return success
        
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
                elif self.get_terrain_type_at(x, y) == Location.MOUNTAIN:
                    layout += "# "
                elif self.get_terrain_type_at(x, y) == Location.WATER:
                    layout += "~ "
                elif self.terrain[y][x] == Location.FENCE:
                    layout += "= "
                elif self.get_terrain_type_at(x, y) == Location.BRIDGE_H:
                    layout += "= "
                elif self.get_terrain_type_at(x, y) == Location.BRIDGE_V:
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
    
    def create_line_terrain(self, terrain_type: int, min_amount: int = 1, max_amount: int = 3) -> None:
        """Creates terrain that extends in straight lines"""
        amount = random.randint(min_amount, max_amount)
        
        for _ in range(amount):
            # Find a random interior passable location for terrain start
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
            terrain_cells = self.extend_line_terrain(terrain_type, start_x, start_y, direction)
            
            # Check if terrain breaks connectivity
            if not self.is_terrain_connected():
                self.punch_terrain_hole(terrain_type, terrain_cells)
    
    def extend_line_terrain(self, terrain_type: int, start_x: int, start_y: int, direction: int) -> list[tuple[int, int]]:
        """Extends a terrain from starting position until obstacles are reached"""
        terrain_cells = []
        
        if direction == 0:  # Horizontal fence
            # Extend left
            x = start_x
            while x >= 1 and self.is_passable(self.terrain[start_y][x]):
                terrain_cells.append((x, start_y))
                self.terrain[start_y][x] = terrain_type
                x -= 1
            
            # Extend right
            x = start_x + 1
            while x < self.width - 1 and self.is_passable(self.terrain[start_y][x]):
                terrain_cells.append((x, start_y))
                self.terrain[start_y][x] = terrain_type
                x += 1
                
        else:  # Vertical fence
            # Extend up
            y = start_y
            while y >= 1 and self.is_passable(self.terrain[y][start_x]):
                terrain_cells.append((start_x, y))
                self.terrain[y][start_x] = terrain_type
                y -= 1
            
            # Extend down
            y = start_y + 1
            while y < self.height - 1 and self.is_passable(self.terrain[y][start_x]):
                terrain_cells.append((start_x, y))
                self.terrain[y][start_x] = terrain_type
                y += 1
        
        return terrain_cells
    
    def punch_terrain_hole(self, terrain_type: int, terrain_cells: list[tuple[int, int]]) -> None:
        """Punches a random hole in the terrain to restore connectivity"""
        if not terrain_cells:
            return
            
        # Try multiple random positions until connectivity is restored
        max_attempts = min(10, len(terrain_cells))
        attempts = 0
        
        # Shuffle terrain cells to try random positions
        terrain_positions = terrain_cells.copy()
        random.shuffle(terrain_positions)
        
        for x, y in terrain_positions:
            if attempts >= max_attempts:
                break
                
            # Temporarily remove terrain piece
            self.terrain[y][x] = Location.GRASS
            
            # Check if connectivity is restored
            if self.is_terrain_connected():
                return  # Hole successfully punched
            else:
                # Restore terrain piece and try next position
                self.terrain[y][x] = terrain_type
                attempts += 1
        
        # If no single hole works, remove the terrain altogether
        for x, y in terrain_cells:
            self.terrain[y][x] = self.base_tile
    
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
                surroundings[i] = self.get_terrain_type(self.get_terrain(x + dx, y + dy))
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
                terrain = self.get_terrain(x, y)
                # if self.get_terrain(x, y) >= Location.WATER:
                # Water should be rotated but I don't have the images yet
                if terrain >= Location.MOUNTAIN or terrain <= Location.BRIDGE_V + 8:
                    self.rotate_obstacle(x, y)


    def create_horizontal_bridge(self, start_x: int, start_y: int, step: int, length: int) -> None:
        for x in range(start_x, start_x + length * step, step):
            if self.get_passable(x, start_y) or self.get_passable(x, start_y + 1):
                return
            else:
                self.terrain[start_y][x] = Location.BRIDGE_H
                self.terrain[start_y + 1][x] = Location.BRIDGE_H
    
    def create_vertical_bridge(self, start_x: int, start_y: int, step: int, length: int) -> None:
        for y in range(start_y, start_y + length * step, step):
            if self.get_passable(start_x, y) or self.get_passable(start_x + 1, y):
                return
            else:
                self.terrain[y][start_x] = Location.BRIDGE_V
                self.terrain[y][start_x + 1] = Location.BRIDGE_V

    def create_bridge(self, direction: int,
                      start_x: int = None, start_y: int = None,
                      base: list[tuple[int, int]] = None,
                      min_length: int = 3, max_length: int = 13) -> None:
        """Extends a bridge from starting position in a straight line.
        Bridge is 2 spaces wide and extends for random length.
        Direction: Location.NORTH, Location.EAST, Location.SOUTH, or Location.WEST
        Starting coordinates are either two values or a 2x2 area.
        The bridge does not modify the terrain at the starting coordinates.
        """
        length = random.randint(min_length, max_length)
        
        if base is not None:
            north, east, south, west = self.get_box_border(base)
        else:
            north = start_y
            south = start_y
            east = start_x
            west = start_x
        
        if direction == Location.NORTH:
            self.create_vertical_bridge(west, north - 1, -1, length)
        elif direction == Location.SOUTH:
            self.create_vertical_bridge(west, south + 1, 1, length)
        elif direction == Location.EAST:
            self.create_horizontal_bridge(east + 1, north, 1, length)
        elif direction == Location.WEST:
            self.create_horizontal_bridge(west - 1, north, -1, length)


    def search_in_line(self, start_x: int, start_y: int, step_x: int, step_y: int,
                       max_search_distance: int = 13) -> tuple[bool, int, int]:
        """Searches in a straight line for passable terrain.
        Returns True if passable terrain is found, False otherwise.
        Returns the distance to the passable terrain, or -1 if no passable terrain is found.
        Returns the terrain type of the passable terrain.
        """
        current_x, current_y = start_x, start_y

        for step in range(1, max_search_distance + 1):
            current_x += step_x
            current_y += step_y
                
            if current_x < 0 or current_x >= self.width or current_y < 0 or current_y >= self.height:
                return (False, -1, None)
            elif self.get_passable(current_x, current_y):
                return (True, step, self.terrain[current_y][current_x])
        return (False, -1, None)

    def check_bridge_viability(self, base: list[tuple[int, int]], direction: int, max_search_distance: int = 13) -> tuple[bool, int]:
        """Checks if bridge construction is viable from a 2x2 starting point.
        
        Searches in a straight line for passable terrain in the specified direction.
        Performs 2 parallel searches (for 2-cell wide bridge) and both must find 
        passable terrain at the same distance and of the same type.
        Checks for passable terrain on the bridges edges.
        If there is any, the bridge is not viable.
        
        Args:
            base: 2x2 starting area
            direction: Direction to search (Location.NORTH, EAST, SOUTH, WEST)
            max_search_distance: Maximum distance to search
            
        Returns:
            tuple: (is_viable, bridge_length) where bridge_length is the distance
                   to passable terrain, or 0 if not viable
        """
        north, east, south, west = self.get_box_border(base)
        
        if direction == Location.EAST:
            search_points = [(east + 1, north), (east + 1, south)]
            outskirts = [(east + 1, north - 1), (east + 1, south + 1)]
            step_x = 1
            step_y = 0        
        elif direction == Location.WEST:
            search_points = [(west - 1, north), (west - 1, south)]
            outskirts = [(west - 1, north - 1), (west - 1, south + 1)]
            step_x = -1
            step_y = 0
        elif direction == Location.NORTH:
            search_points = [(west, north - 1), (east, north - 1)]
            outskirts = [(west - 1, north - 1), (east + 1, north - 1)]
            step_x = 0
            step_y = -1
        elif direction == Location.SOUTH:
            search_points = [(west, south + 1), (east, south + 1)]
            outskirts = [(west - 1, south + 1), (east + 1, south + 1)]
            step_x = 0
            step_y = 1
        else:
            return (False, 0)

        distances = []
        outskirts_distances = []
        terrain_types = []

        for search_x, search_y in search_points:
            success, distance, terrain_type = self.search_in_line(search_x, search_y, step_x, step_y,
                                                                  max_search_distance)
            if not success:
                return (False, 0)
            distances.append(distance)
            terrain_types.append(terrain_type)
        
        for outskirts_x, outskirts_y in outskirts:
            success, outskirts_distance, _ = self.search_in_line(outskirts_x, outskirts_y, step_x, step_y,
                                                                                      max_search_distance)
            outskirts_distances.append(outskirts_distance)

        # Check if both found passable terrain at the same distance
        if distances[0] == distances[1] and terrain_types[0] == terrain_types[1]:
            bridge_length = distances[0]
            
            # If passable terrain was found next to the bridge, bridge is not viable
            if min(outskirts_distances) < bridge_length:
                return (False, 0)
            else:
                return (True, bridge_length)
        else:
            return (False, 0)
    
    def boundary_check(self, x: int, y: int, northwest_gap: int = 0,
                       southeast_gap: int = 0) -> bool:
        """Checks if the coordinates are within the boundaries of the location.
        An additional margin can be enforced.
        """
        if x < northwest_gap or x >= self.width - southeast_gap or \
           y < northwest_gap or y >= self.height - southeast_gap:
            return False
        return True
        
    def attempt_bridge_creation(self, box: list[tuple[int, int]]) -> bool:
        """Attempts to create as many bridges as possible
        from a starting 2x2 area.
        Returns True if at least one bridge was created.
        """
        success = False
        if self.try_erase_terrain_pool(box, Location.ROAD, Location.WATER,
                                       check_only=True, avoid_bridges=True):
            for direction in (Location.NORTH, Location.EAST, Location.SOUTH, Location.WEST):
                bridge_viability = self.check_bridge_viability(box, direction)
                if bridge_viability[0] and bridge_viability[1] > 2:
                    success = True
                    self.create_bridge(direction, base=box,
                                       min_length=bridge_viability[1], max_length=bridge_viability[1])
        if success:
            for x, y in box:
                self.terrain[y][x] = Location.ROAD
        return success

    def connect_passable_terrain(self) -> bool:
        """Connects all passable terrain in the location."""
        for tries in range(1000):
            x = random.randrange(self.width)
            y = random.randrange(self.height)

            if random.random() < 0.5:
                if self.boundary_check(x, y, northwest_gap=1, southeast_gap=2):
                    if self.attempt_bridge_creation(self.get_coordinates_box(x, y)):
                        pass
                        # No prints during gameplay! Still nice during testing.
                        # print(f"Bridge created (attempt {tries})")
                        # print(self.get_layout())                        
                        # input()
            elif self.get_terrain(x, y) == Location.ROAD:
                self.erase_pool(x, y, Location.ROAD, Location.WATER,
                                min_expansions=3, max_expansions=9,
                                avoid_bridges=True)
                # print(f"Land created (attempt {tries})")
                # print(self.get_layout())
                # input()
            if self.is_terrain_connected():
                return True
        return False
    

    def create_regular_location(self) -> None:
        """Modifies the location, using passable terrain as a base.
        Places obstacles of different types."""
        self.terrain = [[self.base_tile for x in range(self.width)] for y in range(self.height)]
        self.create_edges(self.room, self.gap)
        self.expand_edge_pools(ignore_passability=False)

        obstacle_coverage = random.uniform(self.min_obstacle_coverage, self.max_obstacle_coverage)
        
        if random.random() < self.pool_terrain_chance and len(self.pool_terrain_allowed) > 0:
            self.add_pool_terrain(self.get_obstacle(self.pool_terrain_allowed, None))
        
        if random.random() < self.line_terrain_chance and len(self.line_terrain_allowed) > 0:
            self.create_obstacles(obstacle_coverage / 2)
            self.create_line_terrain(self.get_obstacle(self.line_terrain_allowed, None))
            self.create_obstacles(obstacle_coverage / 2)
        else:
            self.create_obstacles(obstacle_coverage)
        
        self.rotate_all_obstacles()


    def create_lake_location(self) -> None:
        """Modifies the location, using inaccessible terrain as a base.
        Ensures all entrances are connected."""
        while True:
            self.terrain = [[self.base_inaccessible_tile for x in range(self.width)] for y in range(self.height)]
            self.create_edges(self.room, self.gap)
            # TODO I should expand those edge pools,
            # but I have to ensure all water terrain is valid
            # So I'll need a different function 
            # self.expand_edge_pools(ignore_passability=True)
            # TODO There are still some issues where water erasal
            # destroys pools and leaves 1x1 tiles.

            if self.connect_passable_terrain():
                break
        
        obstacle_coverage = random.uniform(self.min_obstacle_coverage, self.max_obstacle_coverage)
        self.create_obstacles(obstacle_coverage)
        self.rotate_all_obstacles()
