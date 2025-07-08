import pygame
from mechanics.character import Character

class Unit(Character):
    def __init__(self, name: str, sprite: pygame.Surface, 
                 team: int = 1, grid_x: int = 0, grid_y: int = 0):
        super().__init__(name=name, team=team)
        self.grid_x: int = grid_x
        self.grid_y: int = grid_y
        self.x: int = grid_x * 32
        self.y: int = grid_y * 32
        self.moving: bool = False
        self.back_and_forth: bool = False
        self.direction: tuple[int, int] = (0, 0)
        self.x_offset: int = 0
        self.y_offset: int = 0
        self.base_speed: int = 2
        self.adventure_speed: int = 2
        self.speed_boost: bool = False
        self.alpha: int = 255
        self.sprite: pygame.Surface = sprite
    
    def move(self) -> bool:
        """If the player has initiated movement, keep moving one step.
        Returns True if the player just finished moving to a new tile.
        Returns False if the player is moving or standing still."""
        if not self.moving:
            return False
        
        self.x_offset += self.direction[0] * self.adventure_speed
        self.y_offset += self.direction[1] * self.adventure_speed
        self.x += self.direction[0] * self.adventure_speed
        self.y += self.direction[1] * self.adventure_speed
        
        if abs(self.x_offset) == 32 or abs(self.y_offset) == 32:
            self.grid_x += self.direction[0]
            self.grid_y += self.direction[1]
            self.x_offset = 0
            self.y_offset = 0
            self.moving = False
            return True
        else:
            return False    
    
    def start_movement(self, direction: tuple[int, int]) -> bool:
        """Start moving in the given direction.
        Returns True if the player just started moving.
        Returns False if the player is already moving."""
        if self.moving:
            return False
        else:
            self.moving = True
            self.direction = direction
            self.move()
            return True
        
    def do_back_and_forth(self) -> bool:
        """Animates an initiated back and forth movement.
        Return True if on a direction switch or movement end.
        Return False on ongoing movement or if unit isn't moving."""
        if not self.back_and_forth:
            return False
        
        self.y_offset += self.direction[1] * self.adventure_speed
        self.y += self.direction[1] * self.adventure_speed

        if self.y_offset == 16:
            self.direction = (0, -1)
            return True
        elif self.y_offset == 0:
            self.back_and_forth = False
            return True
        else:
            return False
    
    def start_back_and_forth(self) -> None:
        """Starts a movement animation where the unit goes down and back up."""
        self.back_and_forth = True
        self.direction = (0, 1)
        self.do_back_and_forth()
    
    def set_speed_boost(self, boost: bool) -> None:
        """Enable or disable speed boost (double speed when P is held)"""
        self.speed_boost = boost
        if boost:
            self.adventure_speed = self.base_speed * 2
        else:
            self.adventure_speed = self.base_speed
    
    def set_position(self, x: int, y: int) -> None:
        """Sets the player's position."""
        self.x = x
        self.y = y
    
    def set_grid_position(self, x: int = None, y: int = None) -> None:
        """Sets the player's grid position."""
        if x is not None:
            self.grid_x = x
            self.x = x * 32
        if y is not None:
            self.grid_y = y
            self.y = y * 32
    
    def get_position(self) -> tuple[int, int]:
        """Returns the player's position."""
        return (self.x, self.y)
    
    def get_grid_position(self) -> tuple[int, int]:
        """Returns the player's grid position."""
        return (self.grid_x, self.grid_y)

    def set_alpha(self, alpha: int) -> None:
        """Sets the unit's alpha."""
        self.alpha = alpha
    
    def get_alpha(self) -> int:
        """Returns the unit's alpha."""
        return self.alpha
