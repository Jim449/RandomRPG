from room import Room
from typing import Self, Iterator

class Area():
    def __init__(self, id: int, base_tile: int = 0, allowed_obstacles: tuple[int] = (1, 2, 3, 4),
                 min_obstacle_coverage: float = 0.1, max_obstacle_coverage: float = 0.5,
                 large_obstacles: tuple[int] = (2, 3), large_obstacle_amount: int = 4,
                 base_inaccessible_tile: int = 3, inaccessible_tile_amount: int = 0):
        """Constructs an area, consisting of multiple rooms.
        
        Args:
        id: The id of the area.
        base_tile: Main terrain.
        allowed_obstacles: Obstacles which can be placed.
        min_obstacle_coverage: Minimum obstacle coverage.
        max_obstacle_coverage: Maximum obstacle coverage.
        large_obstacles: Obstacles spanning multiple rooms.
        large_obstacle_amount: Minimum amount of room corners on which to place large obstacles.
        inaccessible_base_tiles: Blocking terrain which is used to cover the majority of a room.
        inaccessible_tile_amount: Amount of rooms in which inaccessible base tiles are placed."""
        self.id: int = id
        self.rooms: list[Room] = []
        self.base_tile: int = base_tile
        self.allowed_obstacles: tuple[int] = allowed_obstacles
        self.min_obstacle_coverage: float = min_obstacle_coverage
        self.max_obstacle_coverage: float = max_obstacle_coverage
        self.large_obstacles: tuple[int] = large_obstacles
        self.large_obstacle_amount: int = large_obstacle_amount
        self.base_inaccessible_tile: int = base_inaccessible_tile
        self.inaccessible_tile_amount: int = inaccessible_tile_amount
    
    def add_room(self, room: Room) -> None:
        self.rooms.append(room)
    
    def remove_room(self, room: Room) -> None:
        self.rooms.remove(room)
    
    def get_rooms(self) -> list[Room]:
        return self.rooms
    
    def construct_locations(self, grid_size: int = 15) -> None:
        """Constructs the locations of the area."""
        for room in self.rooms:
            room.create_location(grid_size, grid_size, 3,
                                 min_obstacle_coverage=self.min_obstacle_coverage,
                                 max_obstacle_coverage=self.max_obstacle_coverage)

    def copy(self) -> Self:
        """Returns a copy of the area. The rooms are not copied."""
        area = Area(self.id, self.base_tile, self.allowed_obstacles, self.min_obstacle_coverage, self.max_obstacle_coverage,
                    self.large_obstacles, self.large_obstacle_amount, self.base_inaccessible_tile, self.inaccessible_tile_amount)
        area.rooms = []
        return area

    def __len__(self) -> int:
        return len(self.rooms)
    
    def __iter__(self) -> Iterator[Room]:
        return iter(self.rooms)
    
    def __next__(self) -> Room:
        return next(self.rooms)