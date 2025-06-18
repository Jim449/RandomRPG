from room import Room
from typing import Self, Iterator

class Area():
    def __init__(self, id: int, base_tile: int = 0, allowed_obstacles: tuple[int] = (1, 2, 3, 4),
                 pool_terrain_chance: float = 0.3, pool_terrain_growth: tuple[int, int] = (0, 2),
                 line_terrain_chance: float = 0.3, line_terrain_amount: tuple[int, int] = (1, 3),
                 obstacle_coverage: tuple[float, float] = (0.1, 0.3),
                 large_obstacles: tuple[int] | None = None, large_obstacle_amount: int = 4,
                 base_inaccessible_tile: int = 3, inaccessible_tile_amount: int = 0):
        """Constructs an area, consisting of multiple rooms.
        
        Args:
        id: The id of the area.
        base_tile: Main terrain.
        allowed_obstacles: Obstacles which can be placed.
        pool_terrain_chance: Chance of placing pool terrain.
        pool_terrain_growth: Minimum and maximum amount of pool terrain to place.
        line_terrain_chance: Chance of placing line terrain.
        line_terrain_amount: Minimum and maximum amount of line terrain to place.
        obstacle_coverage: Minimum and maximum obstacle coverage.
        large_obstacles: Obstacles spanning multiple rooms.
        large_obstacle_amount: Minimum amount of room corners on which to place large obstacles.
        inaccessible_base_tiles: Blocking terrain which is used to cover the majority of a room.
        inaccessible_tile_amount: Amount of rooms in which inaccessible base tiles are placed."""
        self.id: int = id
        self.rooms: list[Room] = []
        self.base_tile: int = base_tile
        self.allowed_obstacles: tuple[int] = allowed_obstacles
        self.pool_terrain_chance: float = pool_terrain_chance
        self.pool_terrain_growth: tuple[int, int] = pool_terrain_growth
        self.line_terrain_chance: float = line_terrain_chance
        self.line_terrain_amount: tuple[int, int] = line_terrain_amount
        self.obstacle_coverage: tuple[float, float] = obstacle_coverage
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
            room.create_location(allowed_obstacles=self.allowed_obstacles,
                                 width=grid_size,
                                 height=grid_size,
                                 gap=3,
                                 pool_terrain_chance=self.pool_terrain_chance,
                                 pool_terrain_growth=self.pool_terrain_growth,
                                 line_terrain_chance=self.line_terrain_chance,
                                 line_terrain_amount=self.line_terrain_amount,
                                 obstacle_coverage=self.obstacle_coverage,
                                 base_tile=self.base_tile)

    def copy(self) -> Self:
        """Returns a copy of the area. The rooms are not copied."""
        area = Area(self.id, self.base_tile, self.allowed_obstacles, self.pool_terrain_chance, self.pool_terrain_growth,
                    self.line_terrain_chance, self.line_terrain_amount, self.obstacle_coverage,
                    self.large_obstacles, self.large_obstacle_amount, self.base_inaccessible_tile, self.inaccessible_tile_amount)
        area.rooms = []
        return area

    def __len__(self) -> int:
        return len(self.rooms)
    
    def __iter__(self) -> Iterator[Room]:
        return iter(self.rooms)
    
    def __next__(self) -> Room:
        return next(self.rooms)