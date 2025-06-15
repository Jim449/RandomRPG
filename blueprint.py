from typing import Self
from room import Room
from random import randrange, shuffle


class Blueprint():
    """A small maze, describing how the areas of a larger maze are connected"""

    def __init__(self, area_count: int, area_length: int):
        """Creates a new, empty blueprint with size equal to area_count"""
        self.area_count: int = area_count
        self.area_length: int = area_length
        self.length: int = area_count
        self.size: int = self.length**2
        self.rooms: list[Room] = []
        self.map: list[list[Room]] = []

    def get_directions(self) -> list[int]:
        """Generates the four compass direction in a random order"""
        directions = [0, 1, 2, 3]
        shuffle(directions)
        return directions

    def sort_by_connections(self) -> None:
        """Sorts rooms so that each room
        is reachable from rooms preceding it in the list"""
        index = 0
        result = [self.rooms[0]]

        while index < len(self.rooms):
            room = result[index]

            for neighbor in self.get_connections(room):
                if neighbor not in result:
                    result.append(neighbor)
            index += 1
        self.rooms = result

    def randomize_areas(self) -> Self:
        """Returns a new blueprint with the same areas and connections,
        but with shuffled area locations"""
        blueprint: Blueprint = Blueprint(self.area_count, self.area_length)
        blueprint.setup()
        blueprint.rooms = []
        available_placements = []
        available_directions = [None]
        self.sort_by_connections()

        # I need a shuffled list of all coordinates in the maze
        for x in range(self.length):
            for y in range(self.length):
                available_placements.append((x, y))
        shuffle(available_placements)

        while len(blueprint.rooms) < len(self.rooms):
            if len(blueprint.rooms) == 0:
                # Select a valid placement for the first room
                placement = available_placements.pop()
                original = self.get_room(0)
                room = blueprint.get_location(*placement)
                room.area = original.area
                room.number = original.number
                blueprint.rooms.append(room)

            # I've ensured this room connects to a room which has already been placed
            # But I still need to figure out which room it connects to
            original = self.get_room(len(blueprint.rooms))

            for neighbor in self.get_connections(original):
                for place in blueprint.rooms:
                    if place.number == neighbor.number:
                        room = place
                        break

            if len(blueprint.rooms) == len(available_directions):
                # Generate a shuffled list of direction for the next room
                directions = self.get_directions()
                available_directions.append(directions)
            else:
                # Here I've failed to place some room
                # Select a direction I haven't tried
                directions = available_directions[len(blueprint.rooms)]

            while True:
                try:
                    dir = directions.pop()

                    try:
                        next_room = blueprint.get_next_location(
                            room.x, room.y, dir)
                    except IndexError:
                        continue

                    if next_room.is_empty():
                        # Success, set as previous room and go on to the next room
                        next_room.area = original.area
                        next_room.number = original.number
                        blueprint.connect_rooms(room.x, room.y, dir)
                        blueprint.rooms.append(next_room)
                        break
                except IndexError:
                    # Failure, out of directions
                    # Stop trying to place this room
                    # Remove the previous room and try to place it somewhere else
                    available_directions.pop()
                    last_room = blueprint.rooms[-1]

                    # Undo everything I've done with this room
                    for dir, path in enumerate(last_room.paths):
                        if path == Room.OPEN:
                            blueprint.connect_rooms(
                                last_room.x, last_room.y, dir, Room.CLOSED)
                    last_room.clear()
                    blueprint.rooms.pop()
                    break
        return blueprint

    def setup(self) -> None:
        """Initializes empty rooms"""
        self.map = []
        self.rooms = []
        index = 0

        for y in range(self.length):
            row = []
            for x in range(self.length):
                room = Room(x, y, number=index, area=index)
                row.append(room)
                self.rooms.append(room)
                index += 1

            self.map.append(row)

    def get_room(self, index: int) -> Room:
        """Returns a room

        Raises:
            IndexError"""
        return self.rooms[index]

    def get_room_of_number(self, number: int) -> Room:
        for room in self.rooms:
            if room.number == number:
                return room

    def get_connections(self, center: Room) -> list[Room]:
        """Returns all rooms connected to the given room"""
        result = []
        for room in self.rooms:
            if room.connected_to(center.number):
                result.append(room)
        return result

    def has_area_connection(self, area_1: int, area_2: int) -> bool:
        """Returns true if area_1 and area_2 are connected"""
        room = self.get_room_of_number(area_1)
        return room.connected_to(area_2)

    def has_area(self, area: int) -> bool:
        """Returns true if there's any room belonging to the given area"""
        for room in self.rooms:
            if room.area == area:
                return True
        return False

    def get_location(self, x: int, y: int) -> Room:
        """Returns the room at (x, y).

        Raises:
            IndexError"""
        return self.map[y][x]

    def get_random_location(self, empty: bool = False) -> Room:
        """Returns a random location"""
        while True:
            x = randrange(self.length)
            y = randrange(self.length)

            if empty == False:
                return self.get_location(x, y)
            elif empty and self.get_location(x, y).is_empty():
                return self.get_location(x, y)

    def get_next_location(self, x: int, y: int, dir: int = None) -> Room:
        """Returns a room adjacent to the room at (x, y).
        Give a direction or None for random

        Raises:
            IndexError"""
        nx = x
        ny = y

        if dir == None:
            dir = randrange(4)

        if dir == Room.NORTH:
            ny = y - 1
        elif dir == Room.EAST:
            nx = x + 1
        elif dir == Room.SOUTH:
            ny = y + 1
        elif dir == Room.WEST:
            nx = x - 1

        if nx == -1 or ny == -1:
            raise IndexError
        else:
            return self.get_location(nx, ny)

    def connect_rooms(self, x: int, y: int, dir: int, connection: int = Room.OPEN) -> None:
        """Create a two-way path between adjacent rooms"""
        room = self.get_location(x, y)

        try:
            next_room = self.get_next_location(x, y, dir)
            room.set_path(dir, connection, next_room.number)
            next_room.set_path(Room.reverse(dir), connection, room.number)
        except IndexError:
            room.set_path(dir, connection, -1)

    def clear_construction_log(self) -> None:
        with open("construction_log.txt", "w") as f:
            f.write("")

    def write_construction_log(self, message: str) -> None:
        with open("construction_log.txt", "a") as f:
            f.write(message)

    def get_layout(self) -> str:
        layout = ""
        for row in self.map:
            for room in row:
                if room.has_path(Room.NORTH):
                    layout += "   |   "
                else:
                    layout += "       "
            layout += "\n"
            for room in row:
                if room.has_path(Room.WEST):
                    layout += "-"
                else:
                    layout += " "
                if room.area == -1:
                    layout += "* * *"
                else:
                    layout += f"{room.area:2}"
                    
                    if room.is_area_connected():
                        layout += f"c{room.area_connection:2}"
                    elif room.is_exchanged():
                        layout += "x  "
                    else:
                        layout += "   "
                if room.has_path(Room.EAST):
                    layout += "-"
                else:
                    layout += " "
            layout += "\n"
            for room in row:
                if room.has_path(Room.SOUTH):
                    layout += "   |   "
                else:
                    layout += "       "
            layout += "\n"
        layout += "\n"
        return layout
    
    @staticmethod
    def main_map_blueprint() -> Self:
        blueprint = Blueprint(3, 3)
        blueprint.setup()
        blueprint.connect_rooms(0, 0, Room.EAST)
        blueprint.connect_rooms(1, 0, Room.SOUTH)
        blueprint.connect_rooms(2, 0, Room.SOUTH)
        blueprint.connect_rooms(0, 1, Room.EAST)
        blueprint.connect_rooms(0, 1, Room.SOUTH)
        blueprint.connect_rooms(1, 1, Room.EAST)
        blueprint.connect_rooms(1, 1, Room.SOUTH)
        blueprint.connect_rooms(2, 1, Room.SOUTH)
        blueprint.connect_rooms(0, 2, Room.EAST)
        # Would connect outside of the map. Which is permissable but I'm not sure if it works
        # blueprint.connect_rooms(0, 2, Room.SOUTH)
        blueprint.connect_rooms(1, 2, Room.EAST)
        return blueprint


if __name__ == "__main__":
    blueprint: Blueprint = Blueprint(3, 3)
    blueprint.setup()
    blueprint.connect_rooms(0, 0, Room.EAST)
    blueprint.connect_rooms(1, 0, Room.EAST)
    blueprint.connect_rooms(1, 0, Room.SOUTH)
    blueprint.connect_rooms(1, 1, Room.EAST)
    blueprint.connect_rooms(1, 1, Room.WEST)
    blueprint.connect_rooms(2, 1, Room.SOUTH)
    blueprint.connect_rooms(0, 1, Room.SOUTH)
    blueprint.connect_rooms(0, 2, Room.EAST)
    print(blueprint.get_layout())
    blueprint.randomize_areas()
