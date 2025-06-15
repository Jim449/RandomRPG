from room import Room
from typing import Self


class Trail():
    """Represents a collection of connected rooms"""

    def __init__(self, id: int, area: int, start: Room):
        """Creates a new trail from the given room"""
        self.rooms: list[Room] = []
        self.id: int = id
        self.area: int = area
        self.finished: bool = False
        self.index: int = 0
        self.connections: list[int] = [id]
        self.add_room(start)

    def add_room(self, room: Room) -> None:
        """Adds a room to this trail"""
        room.trail = self.id
        self.rooms.append(room)

    def connect_trail(self, id: int) -> None:
        """Signals that this trail has connected to another"""
        self.connections.append(id)

    def has_connection(self, id: int) -> bool:
        """Returns true if there's a connection between this trail and another"""
        return id in self.connections

    def __iter__(self) -> Self:
        self.index = len(self.rooms)
        return self

    def __next__(self) -> Room:
        if self.index > 0:
            self.index -= 1
            return self.rooms[self.index]
        else:
            raise StopIteration
