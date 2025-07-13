from room import Room
from location import Location
from typing import Self, Iterator
import random
from encounter import Encounter
from quest_log import QuestLog

class Area():
    def __init__(self, id: int, name: str, base_tile: int = Location.GRASS, allowed_obstacles: tuple[int] = (Location.FOREST, Location.FENCE),
                 pool_terrain_amount: tuple[int, int] = (0, 0), pool_terrain_growth: tuple[int, int] = (0, 2),
                 line_terrain_amount: tuple[int, int] = (0, 0), object_terrain_amount: tuple[int, int] = (0, 0),
                 obstacle_coverage: tuple[float, float] = (0.1, 0.3),
                 large_obstacles: tuple[int] | None = None, large_obstacle_amount: int = 4,
                 large_obstacle_growth: tuple[int, int] = (0, 1),
                 base_inaccessible_tile: int = Location.WATER, inaccessible_tile_amount: int = 0):
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
        self.name: str = name
        self.rooms: list[Room] = []
        self.base_tile: int = base_tile
        self.allowed_obstacles: tuple[int] = allowed_obstacles
        self.pool_terrain_amount: tuple[int, int] = pool_terrain_amount
        self.pool_terrain_growth: tuple[int, int] = pool_terrain_growth
        self.line_terrain_amount: tuple[int, int] = line_terrain_amount
        self.object_terrain_amount: tuple[int, int] = object_terrain_amount
        self.large_obstacle_growth: tuple[int, int] = large_obstacle_growth
        self.obstacle_coverage: tuple[float, float] = obstacle_coverage
        self.large_obstacles: tuple[int] = large_obstacles
        self.large_obstacle_amount: int = large_obstacle_amount
        self.base_inaccessible_tile: int = base_inaccessible_tile
        self.inaccessible_tile_amount: int = inaccessible_tile_amount
        self.encounters: list[Encounter] = []
    
    def add_room(self, room: Room) -> None:
        self.rooms.append(room)
    
    def remove_room(self, room: Room) -> None:
        self.rooms.remove(room)
    
    def get_rooms(self, shuffle: bool = False) -> list[Room]:
        if shuffle:
            rooms = self.rooms.copy()
            random.shuffle(rooms)
            return rooms
        else:
            return self.rooms
    
    def setup_locations(self, grid_size: int = 15) -> None:
        """Sets up the locations of the area."""
        for room in self.rooms:
            room.setup_location(allowed_obstacles=self.allowed_obstacles,
                                 width=grid_size,
                                 height=grid_size,
                                 gap=3,
                                 pool_terrain_amount=self.pool_terrain_amount,
                                 pool_terrain_growth=self.pool_terrain_growth,
                                 line_terrain_amount=self.line_terrain_amount,
                                 object_terrain_amount=self.object_terrain_amount,
                                 corner_terrain_growth=self.large_obstacle_growth,
                                 obstacle_coverage=self.obstacle_coverage,
                                 base_tile=self.base_tile)
    
    def build_locations(self) -> None:
        """Builds the locations of the area."""
        for room in self.rooms:
            room.build_location()
    
    def add_encounter(self, encounter: Encounter) -> None:
        """Adds an encounter to the area."""
        self.encounters.append(encounter)
    
    def get_encounter(self, quest_log: QuestLog) -> Encounter:
        """Returns a random encounter from the area.
        Requirements are checked with the quest log until a valid encounter is found."""
        encounter = random.choices(self.encounters, weights=[party.encounter_weight for party in self.encounters], k=1)[0]
        
        while not encounter.check_requirements(quest_log):
            encounter = random.choices(self.encounters, weights=[party.encounter_weight for party in self.encounters], k=1)[0]
        return encounter

    def copy(self) -> Self:
        """Returns a copy of the area. The rooms are not copied."""
        area = Area(self.id, self.name, 
                    base_tile=self.base_tile,
                    allowed_obstacles=self.allowed_obstacles,
                    pool_terrain_amount=self.pool_terrain_amount,
                    pool_terrain_growth=self.pool_terrain_growth,
                    line_terrain_amount=self.line_terrain_amount,
                    object_terrain_amount=self.object_terrain_amount,
                    large_obstacle_growth=self.large_obstacle_growth,
                    obstacle_coverage=self.obstacle_coverage,
                    large_obstacles=self.large_obstacles,
                    large_obstacle_amount=self.large_obstacle_amount,
                    base_inaccessible_tile=self.base_inaccessible_tile,
                    inaccessible_tile_amount=self.inaccessible_tile_amount)
        area.rooms = []
        area.encounters = self.encounters
        return area

    def __len__(self) -> int:
        return len(self.rooms)
    
    def __iter__(self) -> Iterator[Room]:
        return iter(self.rooms)
    
    def __next__(self) -> Room:
        return next(self.rooms)
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name