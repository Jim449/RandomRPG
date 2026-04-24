from room import Room
from blueprint import Blueprint
from trail import Trail
from random import shuffle, random, randint, choice
from maze_exceptions import IllegalMazeError
from typing import Self
from area import Area

class Maze(Blueprint):
    """A maze"""

    def __init__(self, area_count: int, area_length: int, name: str = None):
        """Generates an empty maze"""
        super().__init__(area_count, area_length)
        self.name: str = name
        self.length: int = area_count * area_length
        self.size: int = self.length**2
        self.areas: list[Area] = []
        self.blueprint: Blueprint = None
        self.trails: list[Trail] = []
    
    def add_area(self, area: Area) -> None:
        """Adds an area to the maze"""
        self.areas.append(area)

    def build_maze(self, blueprint: Blueprint) -> None:
        """Constructs the maze from a blueprint"""
        self.blueprint = blueprint
        blueprint_x = 0
        blueprint_y = 0

        for y in range(self.length):
            row = []
            blueprint_y = y // self.area_length

            for x in range(self.length):
                blueprint_x = x // self.area_length
                room = Room(x, y, number=-1, area=-1)
                area = blueprint.get_location(blueprint_x, blueprint_y).area
                self.set_area(room, area)
                room.exchanged = False
                row.append(room)
                self.rooms.append(room)
            self.map.append(row)

    def get_area(self, id: int, shuffle: bool = False) -> list[Room]:
        """Returns all rooms of a given area.

        Raises:
            IndexError"""
        return self.areas[id].get_rooms(shuffle)
    
    def get_area_link(self, room: Room) -> Room:
        """Returns the external area room that is linked to the given room"""
        area = room.area_connection

        for neighbor in self.get_area(area):
            if neighbor.area_connection == room.area:
                return neighbor
        return None

    def find_area_neighbors(self, room: Room, discovered: set[Room]) -> set[Room]:
        """Search the surroundings for rooms belonging to the same area.
        If this function doesn't locate all rooms of the area,
        it indicates the area has been broken up into distinct parts
        and that it is invalid"""
        for direction in range(4):
            try:
                neighbor = self.get_next_location(room.x, room.y, direction)

                if neighbor.area == room.area and neighbor not in discovered:
                    discovered.add(neighbor)
                    self.find_area_neighbors(neighbor, discovered)
            except IndexError:
                pass
        return discovered

    def check_area_unity(self, id: int) -> bool:
        """Returns true if the area with the given id is valid
        and not broken up into distinct parts"""
        area = self.get_area(id)
        start = area[0]
        discovered = {start}
        discovered = self.find_area_neighbors(start, discovered)
        return len(discovered) == len(area)

    def destroy_area_connection(self, room: Room) -> Room:
        """Destroys the connection to the first external area room.
        Returns the room with the destroyed connection"""
        neighbor = self.get_area_link(room)
        room.set_area_connection(-1)
        neighbor.set_area_connection(-1)
        return neighbor
    
    def restore_area_connection(self, room: Room, neighbor: Room) -> None:
        """Restores a connection between different areas"""
        room.set_area_connection(neighbor.area)
        neighbor.set_area_connection(room.area)

    def restore_area(self, room: Room, old_area: int, new_area: int) -> None:
        """Restores a room to its previous area"""
        room.area = old_area
        room.exchanged = False
        self.areas[new_area].remove_room(room)
        self.areas[old_area].add_room(room)

    def set_area(self, room: Room, area: int) -> None:
        """Assigns an area to a room. If this results in
        an area splitting into distinct parts, an IllegalMazeError is raised.

        Raises:
            IllegalMazeError"""
        old_area = room.area
        room.exchange_to_area(area)

        if old_area == -1:
            self.areas[area].add_room(room)
        else:
            self.areas[old_area].remove_room(room)
            self.areas[area].add_room(room)

            if not self.check_area_unity(old_area):
                raise IllegalMazeError("Area is broken into parts.")

    def get_area_border(self, area_1: int, area_2: int = None,
                        unexchanged_only: bool = False,
                        no_area_connections: bool = False) -> list[tuple[Room, Room, int]]:
        """Returns a list of tuples, containing a room of area_1, a room of area_2
        and a direction linking the rooms together.
        The algorithm checks rooms and direction in a random order.
        If area_2 is None, it represents any area not equal to area_1"""
        area_copy = self.get_area(area_1).copy()
        shuffle(area_copy)

        entries = []

        for room in area_copy:
            for dir in self.get_directions():
                try:
                    neighbor = self.get_next_location(room.x, room.y, dir)

                    if area_2 is None and neighbor.area != area_1:
                        if (unexchanged_only and neighbor.is_exchanged()) or (no_area_connections and (room.is_area_connected() or neighbor.is_area_connected())):
                            continue
                        entries.append((room, neighbor, dir))
                    elif area_2 is not None and neighbor.area == area_2:
                        if (unexchanged_only and neighbor.is_exchanged()) or (no_area_connections and (room.is_area_connected() or neighbor.is_area_connected())):
                            continue
                        entries.append((room, neighbor, dir))
                except IndexError:
                    pass
        return entries

    def link_areas(self, area_1: int, area_2: int) -> None:
        """Attempts to link two areas together.
        Rooms to link are picked at random until a valid connection is found.
        A room cannot link to more than one external area.
        If no valid connection is found, an IllegalMazeError is raised"""
        for room, neighbor, dir in self.get_area_border(area_1, area_2, no_area_connections=True):
            room.set_area_connection(area_2)
            neighbor.set_area_connection(area_1)
            return
        raise IllegalMazeError("Areas couldn't be linked.")

    def expand_from_room(self, room: Room,
                         connect_new_room: bool = False,
                         connect_existing_room: bool = False,
                         connect_trails: bool = False,
                         trail: Trail = None) -> Room:
        """Given a room, returns a random, neighboring room
        and connect the rooms.

        If connect_new_room is true, connect a room which didn't have any previous connections.
        If connect_existing_room is true, connect a room which already had connections.
        If connect_trails, is true: connect a room belonging to a different trail (trail must be provided)
        Returns None if no valid room was found.
        """
        directions = self.get_directions()

        while len(directions) > 0:
            dir = directions.pop()

            try:
                neighbor = self.get_next_location(room.x, room.y, dir)

                if neighbor.area != room.area:
                    continue

                if connect_trails and not trail.has_connection(neighbor.trail):
                    self.connect_rooms(room.x, room.y, dir)
                    return neighbor
                elif connect_new_room and neighbor.is_unconnected():
                    self.connect_rooms(room.x, room.y, dir)
                    return neighbor
                elif connect_existing_room and not room.has_path(dir):
                    self.connect_rooms(room.x, room.y, dir)
                    return neighbor
            except IndexError:
                pass
        return None

    def connect_trails(self) -> None:
        """Expands all trails again in order to connect them"""
        for trail in self.trails:
            for room in trail:
                neighbor = self.expand_from_room(
                    room, connect_trails=True, trail=trail)

                if neighbor != None:
                    trail.connect_trail(neighbor.trail)
                    self.trails[neighbor.trail].connect_trail(trail.id)
                    break
    
    def build_intersections(self, area_id: int) -> None:
        """Adds paths between rooms of the same area"""
        for room in self.get_area(area_id, shuffle=True):
            neighbor = self.expand_from_room(room, connect_existing_room=True)
            if neighbor != None:
                return

    def explore(self, trail: Trail) -> bool:
        """Given a trail of rooms,
        expand with a neighboring,
        previously unconnected room within the same area.
        Returns true if successful"""
        # Trail implements reverse order iteration
        for room in trail:
            addition = self.expand_from_room(room, connect_new_room=True)

            if addition != None:
                trail.add_room(addition)
                return True
        trail.finished = True
        return False

    def construct_areas(self, add_intersections: int = 0) -> None:
        """Constructs the maze by connecting rooms within the same areas.
        Call construct_connections first.
        This will attempt to connect trails as far as possible.
        Then, additional paths can be added within areas,
        depending on the add_intersections parameter."""
        finished = False

        while not finished:
            finished = True

            for trail in self.trails:
                if trail.finished == False:
                    self.explore(trail)
                    finished = False
        self.connect_trails()

        for i in range(add_intersections):
            for area_id in range(len(self.areas)):
                self.build_intersections(area_id)
    
    def get_link_direction(self, room: Room) -> int:
        """Returns the room of a different area that is connected to the given room"""
        for dir in range(4):
            try:
                neighbor = self.get_next_location(room.x, room.y, dir)
                if neighbor.is_area_connected() \
                    and room.area_connection == neighbor.area \
                        and neighbor.area_connection == room.area:
                    return dir
            except IndexError:
                pass
        return None

    def start_trails(self) -> None:
        """Starts trails from all areas"""
        id = 0
        for room in self.rooms:
            if room.is_area_connected():
                self.trails.append(Trail(id, room.area, room))
                id += 1
                dir = self.get_link_direction(room)
                self.connect_rooms(room.x, room.y, dir)


    def construct_connections(self) -> None:
        """Connects areas according to the blueprint.
        Opens up rooms which can be used as starting points
        for further maze expansion"""
        for area_1 in range(self.blueprint.size - 1):
            for area_2 in range(area_1 + 1, self.blueprint.size):
                if self.blueprint.has_area_connection(area_1, area_2):
                    entries = self.get_area_border(area_1, area_2, no_area_connections=True)
                    
                    if len(entries) > 0:
                        room, neighbor, dir = entries[0]
                        room.set_area_connection(neighbor.area)
                        neighbor.set_area_connection(room.area)
                    else:
                        raise IllegalMazeError(f"No available connections between {area_1} and {area_2}")

    def confirm_area_sizes(self, size: int) -> bool:
        """Checks that all areas are of the the correct size"""
        for rooms in self.areas:
            if len(rooms) != size:
                return False
        return True

    def exchange_area_room(self, area: int, max_difference: int, unexchanged_only: bool = True) -> bool:
        """The given area attempts to take a room from another area.
        During the exchange, the following rules must be followed:
        - The area mustn't grow too large in comparison with the other area.
        - The other area mustn't be split into distinct parts.
        - If a connection between two areas is broken, the connection must be replaced."""

        entries = self.get_area_border(area, unexchanged_only=unexchanged_only)
        
        for room, neighbor, dir in entries:
            size_1 = len(self.get_area(area)) + 1
            size_2 = len(self.get_area(neighbor.area)) - 1
            self.write_construction_log(f"Area {area} wants to grab a room from {neighbor.area} for sizes {size_1} to {size_2}, max diff {max_difference}\n")
            old_area = neighbor.area

            if size_1 - size_2 <= max_difference:
                try:
                    # If there is an area connection, I need to place it elsewhere
                    if neighbor.is_area_connected():
                        link = self.destroy_area_connection(neighbor)
                    else:
                        link = None
                    # Change the area
                    self.set_area(neighbor, area)
                    
                    # Move the destroyed area connection
                    if link != None:
                        self.link_areas(old_area, link.area)

                    # Testingtesting!
                    self.write_construction_log(self.get_layout())
                    return True
                except IllegalMazeError as e:
                    # If something fails, restore everything
                    self.restore_area(neighbor, old_area, area)

                    if link != None:
                        self.restore_area_connection(neighbor, link)
                    self.write_construction_log(f"Illegal maze error! {e}\n")
            else:
                self.write_construction_log("Denied!\n")
        return False

    def exchange_rooms(self) -> None:
        """All areas exchanges rooms in order to randomize shapes"""
        area_size = self.area_length**2
        max_difference = 2
        self.clear_construction_log()
        
        # Test with a few tries first
        for tries in range(10):
            for area in range(self.area_count**2):
                exchanged = self.exchange_area_room(area, max_difference, unexchanged_only=True)

                if exchanged == False and len(self.get_area(area)) < self.area_length**2:
                    self.write_construction_log(f"Failed to exchange area of size {len(self.get_area(area))}. Trying again.\n")
                    self.exchange_area_room(area, max_difference, unexchanged_only=False)

            if max_difference > 1:
                max_difference -= 1
            elif self.confirm_area_sizes(area_size):
                return
        raise IllegalMazeError("Failed to exchange rooms evenly")
    
    def expand_inaccessible_tiles(self, room: Room, expansions: int, tile: int) -> int:
        """Expands inaccessible tiles to adjacent rooms.
        Returns the amount of successful expansions."""
        expansion_count = 0

        for dir in self.get_directions():
            try:
                neighbor = self.get_next_location(room.x, room.y, dir)
                if neighbor.area == room.area:
                    neighbor.set_inaccessible_tile(tile)
                    expansion_count += 1
                    if expansion_count == expansions:
                        return expansion_count
            except IndexError:
                pass
        return expansion_count

    def place_inaccessible_tile_in_room(self, room: Room, tile: int, growth: int) -> None:
        """Sets the inaccessible tile of a room.
        If large corner terrain is not set, sets it to the inaccessible tile.
        Expands to adjacent rooms corner terrain.
        """
        room.set_inaccessible_tile(tile)
        for dir in range(4):
            self.place_obstacle_in_room(room, dir, tile, overwrite=False, growth=growth)

    def place_inaccessible_tiles_in_area(self, area: Area) -> None:
        """Places inaccessible tiles in the rooms of the area.
        Rooms are picked at random but adjacent rooms are preferred."""
        rooms = area.get_rooms().copy()
        shuffle(rooms)
        amount = area.inaccessible_tile_amount

        for room in rooms:
            if room.inaccessible_tile is None and amount > 0:
                self.place_inaccessible_tile_in_room(room, area.base_inaccessible_tile, area.large_obstacle_growth)
                amount -= 1
                if amount == 0:
                    return
                amount -= self.expand_inaccessible_tiles(room, randint(0, amount), area.base_inaccessible_tile)
    
    def place_inaccessible_tiles(self) -> None:
        """Places inaccessible tiles in the maze"""
        for area in self.areas:
            if area.inaccessible_tile_amount > 0:
                self.place_inaccessible_tiles_in_area(area)

    def place_obstacle_in_room(self, room: Room, direction: int, obstacle: int, growth: int, overwrite: bool = False) -> None:
        """Places an obstacle in the corner of a room.
        Directions NESW are treated as NE, SE, SW, NW.
        Obstacles will extend to adjacent rooms."""
        if overwrite == False and room.terrain[direction] != None:
            return
        room.set_terrain(direction, obstacle, growth)
        clockwise = ((Room.NORTH, Room.EAST), (Room.EAST, Room.SOUTH), (Room.SOUTH, Room.WEST), (Room.WEST, Room.NORTH))
        directions = ((0, -1), (1, 0), (0, 1), (-1, 0))
        for i, (travel, obstacle_dir) in enumerate(clockwise):
            if obstacle_dir == direction:
                start = (i + 1) % 4
                break
        
        x = room.x
        y = room.y

        for i in range(start, start + 3):
            try:
                travel_dir, obstacle_dir = clockwise[i % 4]
                x += directions[travel_dir][0]
                y += directions[travel_dir][1]
                current_room = self.get_location(x, y)
                current_room.set_terrain(obstacle_dir, obstacle, growth)
            except IndexError:
                pass

    def place_large_obstacles(self) -> None:
        """Places large obstacles according to area settings.
        Affected rooms are picked at random."""
        for area in self.areas:
            if not area.large_obstacles or area.large_obstacle_amount == 0:
                continue
            
            placed = 0

            while placed < area.large_obstacle_amount:
                room = choice(area.get_rooms())
                direction = randint(0, 3)
                obstacle = choice(area.large_obstacles)

                if room.terrain[direction] is None:
                    self.place_obstacle_in_room(room, direction, obstacle,
                                                area.large_obstacle_growth)
                    placed += 1
    
    def setup_locations(self) -> None:
        """Constructs the locations of the maze"""
        for area in self.areas:
            area.setup_locations()
    
    def build_locations(self) -> None:
        """Builds the locations of the maze"""
        for area in self.areas:
            area.build_locations()
    
    def clear_room_numbers(self) -> None:
        """Clears the room numbers of the maze"""
        for room in self.rooms:
            room.number = -1

    def copy(self) -> Self:
        """Returns a copy of the maze"""
        maze = Maze(self.area_count, self.area_length, self.name)
        maze.blueprint = self.blueprint
        maze.map = [[None for x in range(self.length)] for y in range(self.length)]
        maze.trails = self.trails
        maze.areas = [area.copy() for area in self.areas]

        for room in self.rooms:
            room_copy = room.copy()
            maze.rooms.append(room_copy)
            maze.areas[room_copy.area].add_room(room_copy)
            maze.map[room_copy.y][room_copy.x] = room_copy
        return maze
    
    def get_save_game_dict(self):
        """Returns the save game dictionary.
        This contains information about the mazes current appearance."""
        area_data = []
        for area in self.areas:
            area_data.append(area.get_save_game_dict())
        
        room_data = []
        for room in self.rooms:
            room_data.append(room.get_save_game_dict())

        data = {
            "name": self.name,
            "length": self.length,
            "areas": area_data,
            "rooms": room_data
        }


if __name__ == "__main__":
    blueprint = Blueprint(3, 3)
    blueprint.setup()
    blueprint.get_location(0, 0).area = 0
    blueprint.get_location(1, 0).area = 1
    blueprint.get_location(2, 0).area = 2
    blueprint.get_location(0, 1).area = 3
    blueprint.get_location(1, 1).area = 4
    blueprint.get_location(2, 1).area = 5
    blueprint.get_location(0, 2).area = 6
    blueprint.get_location(1, 2).area = 7
    blueprint.get_location(2, 2).area = 8
    blueprint.connect_rooms(0, 0, Room.EAST)
    blueprint.connect_rooms(1, 0, Room.SOUTH)
    blueprint.connect_rooms(1, 1, Room.EAST)
    blueprint.connect_rooms(1, 1, Room.WEST)
    blueprint.connect_rooms(1, 1, Room.SOUTH)
    blueprint.connect_rooms(2, 1, Room.NORTH)
    blueprint.connect_rooms(0, 1, Room.SOUTH)
    blueprint.connect_rooms(0, 2, Room.EAST)
    blueprint.connect_rooms(1, 2, Room.EAST)
    print(blueprint.get_layout())
    maze = Maze(3, 3)
    maze.build_maze(blueprint)
    maze_copy = maze.copy()
    # Construct connections first
    maze.construct_connections()
    print(maze.get_layout())
    # maze.exchange_rooms()
    maze.start_trails()
    maze.construct_areas()
    print(maze.get_layout())
