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
    # Terrain types
    FOREST = 1
    MOUNTAIN = 2
    WATER = 3

    def __init__(self, x: int, y: int, number: int = -1, area: int = -1, trail: int = -1):
        """Creates an empty room at (x, y)"""
        self.x: int = x
        self.y: int = y
        self.number: int = number
        self.area: int = area
        self.trail: int = trail
        self.paths: list[int] = [0, 0, 0, 0]
        self.terrain: list[int] = [Room.FOREST, Room.FOREST, Room.FOREST, Room.FOREST]
        self.connections: list[int] = []
        self.area_connection: int = -1
        self.exchanged: bool = False
        self.location: Location = None

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

    def create_location(self, width: int = 15, height: int = 15, gap: int = 3) -> None:
        """Creates a location for the room"""
        self.location = Location(self, width, height, gap)

    def set_path(self, dir: int, value: int, linked_room: int) -> None:
        """Sets a path towards a direction to OPEN or CLOSED"""
        self.paths[dir] = value
        self.connections.append(linked_room)
    
    def set_terrain(self, dir: int, value: int) -> None:
        """Sets the terrain in a direction
        Direction is increased by 1/8 clockwise, so NORTH (0) is treated as NORTHEAST"""
        self.terrain[dir] = value

    def set_area_connection(self, area: int) -> None:
        """Sets the area connection for the room"""
        self.area_connection = area

    def has_path(self, dir: int) -> bool:
        """Returns true if there is a path towards the given direction"""
        return self.paths[dir] > 0

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


if __name__ == "__main__":
    room = Room(0, 0)
    room.set_path(Room.NORTH, Room.OPEN, 1)
    room.set_path(Room.EAST, Room.OPEN, 2)
    room.set_terrain(Room.NORTH, Room.FOREST)
    room.set_terrain(Room.EAST, Room.FOREST)
    room.set_terrain(Room.SOUTH, Room.FOREST)
    room.set_terrain(Room.WEST, Room.FOREST)
    room.create_location()
    print(room.location.get_layout())
