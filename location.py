import random
from collections import deque
from pool import Pool
from unit import Unit

class Location():
    """Describes a location in the maze.
    A location occupies a single screen."""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    # Expansion types
    EXPAND_POOL = 0 # Must belong to a 2x2 area of similar terrain.
    EXPAND_LINE = 1 # Expands in a line.
    EXPAND_BRIDGE = 2 # Various rules apply.
    SINGLE_TILE = 3 # Single tile obstacle.
    REGULAR_PASSABLE = 4 # Passable terrain.
    IMPORTANT_PASSABLE = 5 # Passable terrain that cannot be modified.
    IMPORTANT_BLOCKING = 6 # Blocking terrain that must be reachable.
    OBJECT = 7 # Object terrain.
    # Terrain types
    BRIDGE_H = -45
    BRIDGE_V = -30
    BRIDGE = -2
    # ROAD = -1
    GRASS = 0
    FOREST = 1
    FENCE = 2
    FENCE_H = 3
    FENCE_V = 4
    SPRITE_STATION = 5
    HOUSE_3x2 = 6
    ANONYMOUS_BLOCKING = 7
    ANONYMOUS_ENTRANCE = 8
    OAK = 9
    WATER = 15
    MOUNTAIN = 30

    def __init__(self, room, allowed_obstacles: tuple[int], width: int = 15, height: int = 15, gap: int = 3,
                 base_tile: int = 0, base_inaccessible_tile: int = None,
                 pool_terrain_amount: tuple[int, int] = (-1, 2), pool_terrain_growth: tuple[int, int] = (0, 2),
                 line_terrain_amount: tuple[int, int] = (-1, 2), corner_terrain_growth: tuple[int, int] = (0, 1),
                 object_terrain_amount: tuple[int, int] = (0, 0),
                 obstacle_coverage: tuple[float, float] = (0.2, 0.4),
                 characters: list[Unit] = None,
                 safe_zone: bool = False):
        """Creates a new location.
        
        Args:
            room: The room that the location belongs to.
            allowed_obstacles: A tuple of allowed obstacles. Excludes large corner obstacles.
            width: The width of the location.
            height: The height of the location.
            gap: The size of the entrance.
            base_tile: The base tile of the location.
            base_inaccessible_tile: A non-passable tile which will be placed across the entire location at creation start.
            pool_terrain_amount: The minimum and maximum amount of pool terrains being placed. Amount is chosen uniformly. Negative values translate to 0.
            pool_terrain_growth: The minimum and maximum number of expansions for a pool terrain. Applies to both large corner terrain and interior terrain.
            line_terrain_amount: The minimum and maximum number of line terrain being placed. Amount is chosen uniformly. Negative values translate to 0.
            object_terrain_amount: The minimum and maximum number of object terrains being placed. Amount is chosen uniformly. Negative values translate to 0.
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
        self.pool_terrain_amount = pool_terrain_amount
        self.pool_terrain_growth = pool_terrain_growth
        self.line_terrain_amount = line_terrain_amount
        self.corner_terrain_growth = corner_terrain_growth
        self.object_terrain_amount = object_terrain_amount
        self.allowed_obstacles = list(allowed_obstacles)
        self.pool_terrain_allowed = []
        self.line_terrain_allowed = []
        self.single_tile_terrain_allowed = []
        self.object_terrain_allowed = []
        self.corners = []
        self.safe_zone = safe_zone

        if characters:
            self.characters = characters
        else:
            self.characters = []
    
    def build_location(self) -> None:
        """Builds the location for the room"""
        for terrain in self.allowed_obstacles:
            expansion_type = self.get_terrain_expansion_type(terrain)
            if expansion_type == Location.EXPAND_POOL:
                self.pool_terrain_allowed.append(terrain)
            elif expansion_type == Location.EXPAND_LINE:
                self.line_terrain_allowed.append(terrain)
            elif expansion_type == Location.SINGLE_TILE:
                self.single_tile_terrain_allowed.append(terrain)
            elif expansion_type == Location.OBJECT:
                self.object_terrain_allowed.append(terrain)

        if self.base_inaccessible_tile:
            self.inaccessible_terrain = True
            self.create_lake_location()
        else:
            self.inaccessible_terrain = False
            self.create_regular_location()
    
    def get_terrain(self, x: int, y: int) -> int:
        """Returns the terrain at the given coordinates"""
        if x < 0 or y < 0:
            raise IndexError("No negative indices allowed")
        return self.terrain[y][x]
    
    def get_passable(self, x: int, y: int) -> bool:
        """Returns True if the terrain at the given coordinates is passable"""
        if x < 0 or y < 0:
            raise IndexError("No negative indices allowed")
        return self.terrain[y][x] <= 0
    
    def get_terrain_type_at(self, x: int, y: int) -> int:
        """Returns the type of terrain at the given coordinates,
        disregarding the rotation of the terrain"""
        if x < 0 or y < 0:
            raise IndexError("No negative indices allowed")
        return self.get_terrain_type(self.terrain[y][x])
    
    def get_terrain_type(self, terrain: int) -> int:
        """Returns the type of terrain.
        The type is the same for all rotations."""
        if terrain >= Location.WATER:
            terrain_type = terrain - terrain % 15
        elif terrain >= Location.BRIDGE_H and terrain < Location.BRIDGE_H + 15:
            terrain_type = Location.BRIDGE_H
        elif terrain >= Location.BRIDGE_V and terrain < Location.BRIDGE_V + 15:
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
        elif terrain_type in (Location.FENCE_H, Location.FENCE_V, Location.FENCE):
            return Location.EXPAND_LINE
        elif terrain == Location.GRASS:
            return Location.REGULAR_PASSABLE
        elif terrain in (Location.SPRITE_STATION, Location.ANONYMOUS_ENTRANCE):
            return Location.IMPORTANT_BLOCKING
        elif terrain in (Location.HOUSE_3x2, Location.OAK, Location.ANONYMOUS_BLOCKING):
            return Location.OBJECT
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

    def _loop_horizontal_edge(self, terrain: int, corner: Pool, start: int, end: int, y: int) -> list[tuple[int, int]]:
        """Loops a horizontal edge from start to end, at y"""
        for x in range(start, end):
            self.terrain[y][x] = terrain
            corner.add_cell(x, y)
    
    def _loop_vertical_edge(self, terrain: int, corner: Pool, start: int, end: int, x: int) -> list[tuple[int, int]]:
        """Loops a vertical edge from start to end, at x"""
        for y in range(start, end):
            self.terrain[y][x] = terrain
            corner.add_cell(x, y)
    
    def create_edges(self) -> None:
        """Creates edges around the room"""
        self.corners = []

        for dir in range(4):
            if self.room.terrain[dir] is not None:
                obstacle = self.room.terrain[dir]
            else:
                obstacle = random.choice(self.single_tile_terrain_allowed)
            corner = Pool(obstacle, self.room.terrain_growth[dir])
            
            if dir == Location.NORTH:
                self._loop_horizontal_edge(obstacle, corner, self.room.get_entrance_end(Location.NORTH), self.width, 0)
                self._loop_vertical_edge(obstacle, corner, 1, self.room.get_entrance_start(Location.EAST), self.width - 1)
            elif dir == Location.EAST:
                self._loop_horizontal_edge(obstacle, corner, self.room.get_entrance_end(Location.SOUTH), self.width, self.height - 1)
                self._loop_vertical_edge(obstacle, corner, self.room.get_entrance_start(Location.EAST), self.height - 1, self.width - 1)
            elif dir == Location.SOUTH:
                self._loop_horizontal_edge(obstacle, corner, 0, self.room.get_entrance_start(Location.SOUTH), self.height - 1)
                self._loop_vertical_edge(obstacle, corner, self.room.get_entrance_end(Location.WEST), self.height - 1, 0)
            elif dir == Location.WEST:
                self._loop_horizontal_edge(obstacle, corner, 0, self.room.get_entrance_start(Location.NORTH), 0)
                self._loop_vertical_edge(obstacle, corner, 1, self.room.get_entrance_start(Location.WEST), 0)

            self.corners.append(corner)

        if self.room.paths[Location.NORTH] == 1:
            for x in range(self.room.get_entrance_start(Location.NORTH), self.room.get_entrance_end(Location.NORTH)):
                self.terrain[0][x] = Location.GRASS
        if self.room.paths[Location.SOUTH] == 1:
            for x in range(self.room.get_entrance_start(Location.SOUTH), self.room.get_entrance_end(Location.SOUTH)):
                self.terrain[self.height - 1][x] = Location.GRASS
        if self.room.paths[Location.WEST] == 1:
            for y in range(self.room.get_entrance_start(Location.WEST), self.room.get_entrance_end(Location.WEST)):
                self.terrain[y][0] = Location.GRASS
        if self.room.paths[Location.EAST] == 1:
            for y in range(self.room.get_entrance_start(Location.EAST), self.room.get_entrance_end(Location.EAST)):
                self.terrain[y][self.width - 1] = Location.GRASS

    @staticmethod
    def is_passable(type: int) -> bool:
        return type <= 0
    
    def is_terrain_connected(self) -> bool:
        """Validates that all passable terrain (0) is reachable using flood fill.
        Also checks that all important blocking terrain is reachable."""
        passable_cells = []
        important_cells = []

        for y in range(self.height):
            for x in range(self.width):
                if self.is_passable(self.terrain[y][x]):
                    passable_cells.append((x, y))
                elif self.get_terrain_expansion_type(self.terrain[y][x]) == Location.IMPORTANT_BLOCKING:
                    important_cells.append((x, y))
        
        # Start flood fill from the first passable cell
        start_x, start_y = passable_cells[0]
        visited = set()
        important_visited = set()
        queue = deque([(start_x, start_y)])
        visited.add((start_x, start_y))
        
        # Directions: North, East, South, West
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        while queue:
            x, y = queue.popleft()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Check bounds and if cell is passable and not visited
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.is_passable(self.terrain[ny][nx]) and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                    elif self.get_terrain_expansion_type(self.terrain[ny][nx]) == Location.IMPORTANT_BLOCKING and (nx, ny) not in important_visited:
                        important_visited.add((nx, ny))
        
        # Check if all passable cells were reached
        return len(visited) == len(passable_cells) and len(important_visited) == len(important_cells)

    def _get_interior_cells(self) -> list[tuple[int, int]]:
        """Returns a list of all interior cells"""
        interior_cells = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.get_terrain_expansion_type(self.terrain[y][x]) == Location.REGULAR_PASSABLE:
                    interior_cells.append((x, y))
        return interior_cells
    
    def create_obstacles(self, obstacle_percentage: float = 0.3) -> None:
        """Creates random obstacles while ensuring all passable terrain remains reachable"""
        
        interior_cells = self._get_interior_cells()
        
        if not interior_cells:
            return
        
        random.shuffle(interior_cells)
        max_obstacles = int(len(interior_cells) * obstacle_percentage)
        
        obstacles_placed = 0
        for x, y in interior_cells:
            if obstacles_placed >= max_obstacles:
                break
            
            terrain_type = random.choice(self.single_tile_terrain_allowed)
            self.terrain[y][x] = terrain_type
            
            if self.is_terrain_connected():
                obstacles_placed += 1
            else:
                self.terrain[y][x] = Location.GRASS
    
    def _place_terrain_in_box(self, x: int, y: int, length: int, height: int, terrain_type: int) -> bool:
        """Places a fixed-size terrain in a box"""
        if x + length >= self.width - 1 or y + height >= self.height - 1:
            return False
        
        # Check if the box is entirely grass
        for col in range(x, x + length):
            for row in range(y, y + height):
                if self.terrain[row][col] != Location.GRASS:
                    return False
        
        for col in range(x, x + length):
            for row in range(y, y + height):
                self.terrain[row][col] = terrain_type

        return True

    def place_object(self, x: int, y: int, terrain_type: int) -> bool:
        """Places a fixed-size object at the given coordinates"""
        length = 0
        height = 0
        entrance_x = None
        entrance_y = None
        
        if terrain_type == Location.HOUSE_3x2:
            length = 3
            height = 2
            entrance_x = x + 1
            entrance_y = y + 1
        elif terrain_type == Location.OAK:
            length = 2
            height = 2

        if not self._place_terrain_in_box(x, y, length, height, Location.ANONYMOUS_BLOCKING):
            return False
        
        self.terrain[y][x] = terrain_type
        
        # Ensures the entrance is reachable
        if entrance_y is not None:
            self.terrain[entrance_y][entrance_x] = Location.ANONYMOUS_ENTRANCE

        if self.is_terrain_connected():
            return True
        else:
            self._place_terrain_in_box(x, y, length, height, Location.GRASS)
            return False
    
    def create_objects(self) -> None:
        """Creates random objects while ensuring all passable terrain remains reachable"""
        interior_cells = self._get_interior_cells()
        
        if not interior_cells:
            return
        
        random.shuffle(interior_cells)
        max_objects = random.randint(self.object_terrain_amount[0], self.object_terrain_amount[1])

        objects_placed = 0
        for x, y in interior_cells:
            if objects_placed >= max_objects:
                break

            terrain_type = random.choice(self.object_terrain_allowed)

            if self.place_object(x, y, terrain_type):
                objects_placed += 1
    
    def place_character(self, character: Unit, interior_cells: list[tuple[int, int]]) -> None:
        """Places a character at a random interior cell"""
        while True:
            i = random.randrange(len(interior_cells))
            x, y = interior_cells[i]
            self.terrain[y][x] = Location.SPRITE_STATION
            character.set_grid_position(x, y)
            interior_cells.pop(i)
            
            if self.is_terrain_connected():
                return
            else:
                self.terrain[y][x] = Location.GRASS

    def place_all_characters(self) -> None:
        """Places characters at random."""
        interior_cells = self._get_interior_cells()

        for character in self.characters:
            self.place_character(character, interior_cells)
    
    def get_character_at(self, x: int, y: int) -> Unit:
        """Returns the character at the given coordinates, or None if there is none."""
        for character in self.characters:
            if character.get_grid_position() == (x, y):
                return character
        return None
    
    def get_random_position(self) -> tuple[int, int]:
        """Returns a random passable position in the location."""
        while True:
            x = random.randrange(1, self.width - 1)
            y = random.randrange(1, self.height - 1)
            if self.is_passable(self.terrain[y][x]):
                return (x, y)

    def get_nearby_character(self, x: int, y: int) -> Unit:
        """Returns a character within conversation range of the given coordinates,
        or None if there is none."""
        directions = ((0, -1), (1, 0), (0, 1), (-1, 0))
        for dx, dy in directions:
            character = self.get_character_at(x + dx, y + dy)
            if character is not None:
                return character
        return None

    def expand_pool(self, pool: Pool,
                    check_passability: bool = False,
                    avoid_bridges: bool = False,
                    erased_terrain: int = None) -> None:
        """Expands a specific pool of terrain type"""
        max_steps = pool.growth * 10
        expansions_made = 0
        step = 0
        offset = ((0, 0), (-1, 0), (0, -1), (-1, -1))
        
        while expansions_made < pool.growth and step < max_steps:
            coordinates = pool.get_cell()
            random_offset = random.choice(offset)
            current_x = max(0, min(self.width - 2, coordinates[0] + random_offset[0]))
            current_y = max(0, min(self.height - 2, coordinates[1] + random_offset[1]))
            pool_coords = self.get_coordinates_box(current_x, current_y)

            if self.place_pool(pool_coords, pool.terrain,
                               allow_addition=True,
                               allow_extension=True,
                               check_only=False,
                               check_passability=check_passability,
                               avoid_bridges=avoid_bridges,
                               erased_terrain=erased_terrain)[0]:
                expansions_made += 1
                pool.add_box(pool_coords)
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

    def place_pool(self, pool_coords: list[tuple[int, int]],
                   terrain: int,
                   allow_addition: bool = True,
                   allow_extension: bool = True,
                   erased_terrain: int = None,
                   check_only: bool = False,
                   check_passability: bool = False,
                   avoid_bridges: bool = False) -> tuple[bool, bool]:
        """Places a 2x2 pool of terrain. Can be used to place pool-type terrain
        or overwrite existing pool-type terrain with arbitrary terrain.
        Returns a tuple of booleans. The first is True if a pool could be placed.
        The second is True if the pool was a new addition
        and False if it was an extension of existing pool terrain.
        If a pool couldn't be placed, the second return value will be None.

        Args:
            pool_coords: list of coordinates to place the pool
            terrain: terrain type to place
            allow_addition: if True, allow adding new, isolated terrain
            allow_extension: if True, allow extending existing pool terrain
            erased_terrain: if provided, replace existing pool terrain of this type. No other terrain can be replaced
            check_only: if True, terrain is not actually placed
            check_passability: if True, check if all passable terrain is connected
            avoid_bridges: if True, avoid placing terrain next to bridges
        """
        north, east, south, west = self.get_box_border(pool_coords)
        terrain_count = 0
        erased_count = 0
        existing_terrain = []
        success = True
        new_addition = True

        for x, y in pool_coords:
            replaced_terrain = self.get_terrain_type_at(x, y)
            on_edge = (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1)
            existing_terrain.append((x, y, replaced_terrain))
            
            if on_edge and replaced_terrain != terrain:
                return (False, None)
            
            if replaced_terrain == terrain:
                terrain_count += 1
                new_addition = False
            elif erased_terrain is not None: 
                if replaced_terrain == erased_terrain:
                    erased_count += 1
                else:
                    return (False, None)
            elif erased_terrain is None:
                if not self.is_passable(replaced_terrain):
                    return (False, None)
        
        if erased_terrain is not None and erased_count == 0:
            return (False, None)
        if not allow_extension and not new_addition:
            return (False, None)
        
        # Try placing the terrain
        for x, y in pool_coords:
            self.terrain[y][x] = terrain
        
        frame = [(west, north - 1), (east, north - 1),
                 (west, south + 1), (east, south + 1),
                 (west - 1, north), (west - 1, south),
                 (east + 1, north), (east + 1, south)]
        
        for x, y in frame:
            try:
                frame_terrain = self.get_terrain(x, y)
            except IndexError:
                break

            # Failure if pool is next to bridge
            if avoid_bridges and self.get_terrain_expansion_type(frame_terrain) == Location.EXPAND_BRIDGE:
                success = False
                break
            # Failure if erasure causes invalid 1-width pool
            if erased_terrain is not None and not self.validate_pool(x, y):
                success = False
                break
            # Frame terrain is accounted for when checking for new addition
            if new_addition and frame_terrain == terrain:
                new_addition = False

        if new_addition and not allow_addition:
            success = False
        elif not new_addition and not allow_extension:
            success = False

        if success and check_passability:
            success = self.is_terrain_connected()

        # Revert
        if not success or check_only:
            for x, y, original in existing_terrain:
                self.terrain[y][x] = original
        
        if success:
            return (True, new_addition)
        else:
            return (False, None)

    def get_layout(self) -> str:
        layout = ""
        for y in range(self.height):
            for x in range(self.width):
                if self.terrain[y][x] == Location.FOREST:
                    layout += "$ "
                elif self.terrain[y][x] == Location.GRASS:
                    layout += ", "
                elif self.get_terrain_type_at(x, y) == Location.MOUNTAIN:
                    layout += "# "
                elif self.get_terrain_type_at(x, y) == Location.WATER:
                    layout += "~ "
                elif self.terrain[y][x] == Location.FENCE_H:
                    layout += "= "
                elif self.terrain[y][x] == Location.FENCE_V:
                    layout += "| "
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
    
    def create_line_terrain(self, terrain_type: int, amount: int = 1) -> None:
        """Creates terrain that extends in straight lines"""
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
                self.punch_terrain_hole(terrain_type + direction + 1, terrain_cells)
    
    def extend_line_terrain(self, terrain_type: int, start_x: int, start_y: int, direction: int) -> list[tuple[int, int]]:
        """Extends a terrain from starting position until obstacles are reached"""
        terrain_cells = []
        
        if direction == 0:  # Horizontal fence
            # Extend left
            x = start_x
            while x >= 1 and self.is_passable(self.terrain[start_y][x]):
                terrain_cells.append((x, start_y))
                self.terrain[start_y][x] = terrain_type + 1
                x -= 1
            
            # Extend right
            x = start_x + 1
            while x < self.width - 1 and self.is_passable(self.terrain[start_y][x]):
                terrain_cells.append((x, start_y))
                self.terrain[start_y][x] = terrain_type + 1
                x += 1
                
        else:  # Vertical fence
            # Extend up
            y = start_y
            while y >= 1 and self.is_passable(self.terrain[y][start_x]):
                terrain_cells.append((start_x, y))
                self.terrain[y][start_x] = terrain_type + 2
                y -= 1
            
            # Extend down
            y = start_y + 1
            while y < self.height - 1 and self.is_passable(self.terrain[y][start_x]):
                terrain_cells.append((start_x, y))
                self.terrain[y][start_x] = terrain_type + 2
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
        Assumes the obstacle has no more than 2 borders to other types of terrain.
        Replaces obstacle number with obstacle number + rotation.

        There are 14 possible rotations:
        8 outward rotations, where the obstacle neighbors different types of terrain
        orthagonally. Numbered 1 to 8 starting with north,
        rotating clockwise in eights.
        4 inward rotations, where the obstacle neighbors different types of terrain
        diagonally. Numbered 9 to 12 starting with northeast,
        rotating clockwise in fourths.
        2 double inward rotations, where the obstacle neighbors different terrain
        diagonally on both sides."""
        obstacle = self.get_terrain(x, y)
        straight = ((0, -1), (1, 0), (0, 1), (-1, 0))
        diagonal = ((1, -1), (1, 1), (-1, 1), (-1, -1))
        straight_surroundings = [None, None, None, None]
        diagonal_surroundings = [None, None, None, None]

        for i, (dx, dy) in enumerate(straight):
            try:
                straight_surroundings[i] = self.get_terrain_type_at(x + dx, y + dy)
                # Treating bridges as water so that bridges don't cause shorelines
                if obstacle == Location.WATER and straight_surroundings[i] in (Location.BRIDGE_H, Location.BRIDGE_V):
                    straight_surroundings[i] = Location.WATER
            except IndexError:
                straight_surroundings[i] = obstacle
        
        for i, (dx, dy) in enumerate(diagonal):
            try:
                diagonal_surroundings[i] = self.get_terrain_type_at(x + dx, y + dy)
                if obstacle == Location.WATER and diagonal_surroundings[i] in (Location.BRIDGE_H, Location.BRIDGE_V):
                    diagonal_surroundings[i] = Location.WATER
            except IndexError:
                diagonal_surroundings[i] = obstacle
        
        if obstacle != straight_surroundings[0] and obstacle != straight_surroundings[3]:
            self.terrain[y][x] = obstacle + 8
            return
        
        # Treating north as 1, each one eight step clockwise adds 1
        # I've checked northwest. Therefore, if north but not northeast,
        # I can deduce north
        for i in range(4):
            if i < 3 and obstacle != straight_surroundings[i] and obstacle != straight_surroundings[i + 1]:
                self.terrain[y][x] = obstacle + 2*i + 2
                return
            elif obstacle != straight_surroundings[i]:
                # Accounting for a special case
                # where I want to split a mountain into two
                if (obstacle != diagonal_surroundings[(i+1)%4]) \
                    or ():
                    self.terrain[y][x] = obstacle + 2*i + 2
                elif obstacle != diagonal_surroundings[(i+2)%4]:
                    addition = 2*i if i > 0 else 8
                    self.terrain[y][x] = obstacle + addition
                else:
                    self.terrain[y][x] = obstacle + 2*i + 1
                return
        
        if obstacle in (Location.BRIDGE_H, Location.BRIDGE_V):
            return
        
        # Checking for double diagonal slopes
        if obstacle != diagonal_surroundings[0] and obstacle != diagonal_surroundings[2]:
            self.terrain[y][x] = obstacle + 13
            return
        elif obstacle != diagonal_surroundings[1] and obstacle != diagonal_surroundings[3]:
            self.terrain[y][x] = obstacle + 14
            return
        
        # Checking for single diagonal slopes
        # I'll number these 9 to 12
        for i, (dx, dy) in enumerate(diagonal):
            if obstacle != diagonal_surroundings[i]:
                self.terrain[y][x] = obstacle + 9 + i
                return

    def rotate_all_obstacles(self) -> None:
        """Rotates all obstacles in the location."""
        for y in range(self.height):
            for x in range(self.width):
                terrain = self.get_terrain(x, y)
                if terrain >= Location.WATER or terrain < Location.BRIDGE_V + 15:
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
        Returns the distance to the passable terrain, or 100 if no passable terrain is found.
        Returns the terrain type of the passable terrain.
        """
        current_x, current_y = start_x, start_y

        for step in range(1, max_search_distance + 1):
            current_x += step_x
            current_y += step_y
            
            if current_x < 0 or current_x >= self.width or current_y < 0 or current_y >= self.height:
                # Returning a high distance should be easier to work with than None
                # as it will make the outskirts check succeed
                return (False, 100, None)
            elif self.get_passable(current_x, current_y):
                return (True, step, self.terrain[current_y][current_x])
        return (False, 100, None)

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
        if distances[0] == distances[1] \
            and self.get_terrain_expansion_type(terrain_types[0]) == Location.REGULAR_PASSABLE \
                and self.get_terrain_expansion_type(terrain_types[1]) == Location.REGULAR_PASSABLE:
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
        if self.place_pool(box, Location.GRASS,
                           allow_addition=True, allow_extension=True,
                           erased_terrain=Location.WATER,
                           check_only=True,
                           check_passability=False,
                           avoid_bridges=True)[0]:
            for direction in (Location.NORTH, Location.EAST, Location.SOUTH, Location.WEST):
                bridge_viability = self.check_bridge_viability(box, direction)
                if bridge_viability[0] and bridge_viability[1] > 2:
                    success = True
                    self.create_bridge(direction, base=box,
                                       min_length=bridge_viability[1], max_length=bridge_viability[1])
        if success:
            for x, y in box:
                self.terrain[y][x] = Location.GRASS
        return success

    def connect_passable_terrain(self, attempts: int = 300) -> bool:
        """Connects all passable terrain in the location."""
        for tries in range(attempts):
            x = random.randrange(self.width - 1)
            y = random.randrange(self.height - 1)

            if random.random() < 0.5:
                if self.boundary_check(x, y, northwest_gap=1, southeast_gap=2):
                    if self.attempt_bridge_creation(self.get_coordinates_box(x, y)):
                        pass
                        # No prints during gameplay! Still nice during testing.
                        # print(f"Bridge created (attempt {tries})")
                        # print(self.get_layout())                        
                        # input()
            else: # self.get_terrain(x, y) == Location.ROAD:
                if self.place_pool(self.get_coordinates_box(x, y), Location.GRASS,
                                allow_addition=False, allow_extension=True,
                                erased_terrain=self.base_inaccessible_tile,
                                check_passability=False, avoid_bridges=True)[0]:
                    pass
                    # print(f"Land created (attempt {tries})")
                    # print(self.get_layout())
                    # input()
                # self.erase_pool(x, y, Location.ROAD, Location.WATER,
                #                 min_expansions=3, max_expansions=9,
                #                 avoid_bridges=True)
                # print(f"Land created (attempt {tries})")
                # print(self.get_layout())
                # input()
            if self.is_terrain_connected():
                return True
        return False
    

    def build_pools(self, amount: int, allowed_terrain: list[int],
                    erased_terrain: int = None, check_passability: bool = False,
                    avoid_bridges: bool = False) -> None:
        tries = amount * 100

        while amount > 0 and tries > 0:
            x = random.randrange(1, self.width - 2)
            y = random.randrange(1, self.height - 2)
            terrain = random.choice(allowed_terrain)
            box = self.get_coordinates_box(x, y)
            
            if self.place_pool(box, terrain,
                               allow_addition=True,
                               allow_extension=False,
                               erased_terrain=erased_terrain,
                               check_only=False,
                               check_passability=check_passability,
                               avoid_bridges=avoid_bridges)[0]:
                amount -= 1
                pool = Pool(terrain, self.pool_terrain_growth)
                pool.add_box(box)
                self.expand_pool(pool,
                                 check_passability=check_passability,
                                 avoid_bridges=avoid_bridges,
                                 erased_terrain=erased_terrain)
            tries -= 1
    

    def add_random_land(self) -> None:
        """Randomly adds a new pool of land."""
        while True:
            x = random.randrange(1, self.width - 2)
            y = random.randrange(1, self.height - 2)
            if self.place_pool(self.get_coordinates_box(x, y), Location.GRASS,
                                allow_addition=True,
                                allow_extension=False,
                                erased_terrain=Location.WATER,
                                check_passability=False)[0]:
                return


    def create_regular_location(self) -> None:
        """Modifies the location, using passable terrain as a base.
        Places obstacles of different types."""
        while True:
            self.terrain = [[self.base_tile for x in range(self.width)] for y in range(self.height)]
            # Create and expand corner obstacles
            self.create_edges()
            self.create_objects()
            try:
                self.place_all_characters()
            except ValueError as e:
                continue

            for i in range(4):
                self.expand_pool(self.corners[i], check_passability=True, avoid_bridges=False)
            
            obstacle_coverage = random.uniform(self.min_obstacle_coverage, self.max_obstacle_coverage)
            pool_amount = random.randint(self.pool_terrain_amount[0], self.pool_terrain_amount[1])
            line_amount = random.randint(self.line_terrain_amount[0], self.line_terrain_amount[1])

            # Create large internal obstacles
            self.build_pools(pool_amount, self.pool_terrain_allowed,
                            erased_terrain=None,
                            check_passability=True,
                            avoid_bridges=False)
            
            if line_amount > 0:
                # If there are fences,
                # I create some small obstacles for them to collide with
                # That should make them shorter
                self.create_obstacles(obstacle_coverage / 2)
                self.create_line_terrain(self.get_obstacle(self.line_terrain_allowed, None), line_amount)
                self.create_obstacles(obstacle_coverage / 2)
            else:
                self.create_obstacles(obstacle_coverage)
            
            self.rotate_all_obstacles()
            return
            


    def create_lake_location(self) -> None:
        """Modifies the location, using inaccessible terrain as a base.
        Ensures all entrances are connected."""
        while True:
            self.terrain = [[self.base_inaccessible_tile for x in range(self.width)] for y in range(self.height)]
            self.create_edges()
            try:
                self.place_all_characters()
            except ValueError as e:
                continue

            # Create land until all entrances are connected
            # If there's only one entrance, create some more land
            # to get more interesting terrain
            if self.room.count_paths() == 1:
                self.add_random_land()

            if self.connect_passable_terrain():
                break
        
        # Expand large corner obstacles
        for i in range(4):
            self.expand_pool(self.corners[i], check_passability=False, avoid_bridges=True,
                             erased_terrain=self.base_inaccessible_tile)
        
        pool_amount = random.randint(self.pool_terrain_amount[0], self.pool_terrain_amount[1])
        
        # Add more obstacles in the middle
        # These can only be placed on water
        # Notably, obstacles will be surrounded by grass
        # meaning I can't place them next to bridges
        self.build_pools(pool_amount, self.pool_terrain_allowed,
                         check_passability=False,
                         erased_terrain=self.base_inaccessible_tile,
                         avoid_bridges=True)
        
        # Adds small obstacles on land
        obstacle_coverage = random.uniform(self.min_obstacle_coverage, self.max_obstacle_coverage)
        self.create_obstacles(obstacle_coverage)
        self.rotate_all_obstacles()
