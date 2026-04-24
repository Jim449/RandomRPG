from typing import Self
from location import Location

class Room():
    """Describes a maze room"""
    OPEN: int = 1
    CLOSED: int = 0
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def __init__(self, x: int, y: int, number: int = -1, area: int = -1, trail: int = -1):
        """Creates an empty room at (x, y)"""
        self.x: int = x
        self.y: int = y
        self.number: int = number
        self.area: int = area
        self.trail: int = trail
        self.paths: list[int] = [0, 0, 0, 0]
        self.terrain: list[int] = [None, None, None, None]
        self.entrances: list[tuple[int, int]] = [(6, 9), (6, 9), (6, 9), (6, 9)]
        self.terrain_growth: list[int] = [0, 0, 0, 0]
        self.connections: list[int] = []
        self.area_connection: int = -1
        self.exchanged: bool = False
        self.location: Location = None
        self.inaccessible_tile: int = None

    def get_type(self) -> str:
        """Returns the types of path NESW.
        Equals the name of the room image"""
        result = ""

        for path in self.paths:
            if path > 0:
                result = "1" + result
            else:
                result = "0" + result
        return result

    def setup_location(self, allowed_obstacles: tuple[int], width: int = 15, height: int = 15, gap: int = 3,
                        pool_terrain_amount: tuple[int, int] = (0, 0), pool_terrain_growth: tuple[int, int] = (0, 2),
                        line_terrain_amount: tuple[int, int] = (1, 3), object_terrain_amount: tuple[int, int] = (0, 0),
                        corner_terrain_growth: tuple[int, int] = (0, 1),
                        base_tile: int = 0,
                        obstacle_coverage: tuple[float, float] = (0.2, 0.4)) -> None:
        """Sets up a location for the room.
        The location can be built using build_location().
        Until then, any location details can be changed."""
        self.location = Location(self,
                                 allowed_obstacles=allowed_obstacles,
                                 width=width,
                                 height=height,
                                 gap=gap,
                                 pool_terrain_amount=pool_terrain_amount,
                                 pool_terrain_growth=pool_terrain_growth,
                                 line_terrain_amount=line_terrain_amount,
                                 object_terrain_amount=object_terrain_amount,
                                 corner_terrain_growth=corner_terrain_growth,
                                 obstacle_coverage=obstacle_coverage,
                                 base_tile=base_tile,
                                 base_inaccessible_tile=self.inaccessible_tile)
    
    def build_location(self) -> None:
        """Builds the location for the room"""
        self.location.build_location()

    def set_path(self, dir: int, value: int, linked_room: int) -> None:
        """Sets a path towards a direction to OPEN or CLOSED"""
        self.paths[dir] = value
        
        if value > 0:
            self.connections.append(linked_room)
        elif linked_room in self.connections:
            self.connections.remove(linked_room)
    
    def set_terrain(self, dir: int, value: int, growth: int = 5) -> None:
        """Sets the terrain in a direction
        Direction is increased by 1/8 clockwise, so NORTH (0) is treated as NORTHEAST"""
        self.terrain[dir] = value
        self.terrain_growth[dir] = growth

    def set_area_connection(self, area: int) -> None:
        """Sets the area connection for the room"""
        self.area_connection = area

    def has_path(self, dir: int) -> bool:
        """Returns true if there is a path towards the given direction"""
        return self.paths[dir] > 0
    
    def count_paths(self) -> int:
        """Returns the number of paths"""
        amount = 0
        for path in self.paths:
            if path > 0:
                amount += 1
        return amount

    def connected_to(self, room_number: int) -> bool:
        """Returns true if there is a direct path from this room
        to the room with the given room number"""
        return room_number in self.connections
    
    def exchange_to_area(self, area: int) -> None:
        """Exchanges the room to the given area"""
        self.area = area
        self.exchanged = True

    def is_area_connected(self) -> bool:
        """Returns true if the room connects to another area"""
        return self.area_connection != -1

    def is_exchanged(self) -> bool:
        """Returns true if the room has been exchanged"""
        return self.exchanged
    
    def set_main_tile(self, tile: int) -> None:
        """Sets the main tile of the room"""
        self.main_tile = tile
    
    def set_inaccessible_tile(self, tile: int) -> None:
        """Sets the inaccessible tile of the room"""
        self.inaccessible_tile = tile
    
    def get_entrance_start(self, dir: int) -> int:
        if self.paths[dir] == Room.OPEN:
            return self.entrances[dir][0]
        else:
            return (self.entrances[dir][0] + self.entrances[dir][1]) // 2

    def get_entrance_end(self, dir: int) -> int:
        if self.paths[dir] == Room.OPEN:
            return self.entrances[dir][1]
        else:
            return (self.entrances[dir][0] + self.entrances[dir][1]) // 2

    def clear(self) -> None:
        """Clears paths, number and area"""
        self.paths = [0, 0, 0, 0]
        self.connections = []
        self.area_connections = []
        self.exchanged = False
        self.number = -1
        self.area = -1

    def is_empty(self) -> bool:
        """Returns true if room details haven't been set"""
        return self.area == -1

    def is_unconnected(self) -> bool:
        """Returns true if room doesn't connect to any other room"""
        return len(self.connections) == 0

    def copy(self) -> Self:
        """Returns a copy of the room"""
        room = Room(self.x, self.y, self.number, self.area, self.trail)
        room.paths = self.paths.copy()
        room.connections = self.connections.copy()
        room.area_connection = self.area_connection
        room.exchanged = self.exchanged
        return room

    @staticmethod
    def reverse(dir: int) -> int:
        """Returns the reverse direction"""
        return (dir + 2) % 4
    
    def get_save_game_dict(self) -> dict:
        """Returns a dictionary describing the rooms current appearence.
        Instructions for creating the room aren't saved"""
        data = {
            "x": self.x,
            "y": self.y,
            "number": self.number,
            "area": self.area,
            "paths": self.paths,
            "location": self.location.get_save_game_dict()
        }
        return data


if __name__ == "__main__":
    room = Room(0, 0)
    room.set_path(Room.NORTH, Room.OPEN, 1)
    room.set_path(Room.EAST, Room.OPEN, 2)
    room.set_terrain(Room.NORTH, Location.MOUNTAIN)
    room.set_terrain(Room.EAST, Location.MOUNTAIN)
    room.set_terrain(Room.SOUTH, Location.MOUNTAIN)
    room.set_terrain(Room.WEST, Location.MOUNTAIN)
    # room.set_inaccessible_tile(Location.WATER)
    room.create_location(allowed_obstacles=(Location.FOREST, Location.MOUNTAIN),
                         pool_terrain_amount=(0, 0), pool_terrain_growth=(0, 4),
                         line_terrain_amount=(0, 0),
                         obstacle_coverage=(0.2, 0.2))
    print(room.location.get_raw_layout())
    print()
    print(room.location.get_layout())
