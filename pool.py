from random import choice, randint

class Pool():
    """Describes a collection of cells with a specific terrain.
    This terrain can be expanded
    depending on a growth value.
    """
    def __init__(self, terrain: int, growth: tuple[int, int] | int = 0):
        self.terrain = terrain
        if isinstance(growth, tuple):
            self.growth = randint(growth[0], growth[1])
        else:
            self.growth = growth
        self.cells = []
    
    def add_cell(self, x: int, y: int) -> None:
        if (x, y) not in self.cells:
            self.cells.append((x, y))
    
    def add_box(self, box: list[tuple[int, int]]) -> None:
        for cell in box:
            self.add_cell(cell[0], cell[1])
    
    def remove_cell(self, x: int, y: int) -> None:
        self.cells.remove((x, y))
    
    def get_cell(self) -> tuple[int, int]:
        return choice(self.cells)
    
