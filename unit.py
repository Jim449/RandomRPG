import pygame

class Unit():
    def __init__(self, sprite: pygame.Surface, x: int = 0, y: int = 0):
        self.x: int = x
        self.y: int = y
        self.moving: bool = False
        self.direction: tuple[int, int] = (0, 0)
        self.x_offset: int = 0
        self.y_offset: int = 0
        self.base_speed: int = 2
        self.speed: int = 2
        self.speed_boost: bool = False
        self.sprite: pygame.Surface = sprite
    
    def move(self) -> bool:
        """If the player has initiated movement, keep moving one step.
        Returns True if the player just finished moving to a new tile.
        Returns False if the player is moving or standing still."""
        if not self.moving:
            return False
        
        self.x_offset += self.direction[0] * self.speed
        self.y_offset += self.direction[1] * self.speed
        
        if abs(self.x_offset) == 32 or abs(self.y_offset) == 32:
            self.x += self.direction[0]
            self.y += self.direction[1]
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
    
    def set_speed_boost(self, boost: bool) -> None:
        """Enable or disable speed boost (double speed when P is held)"""
        self.speed_boost = boost
        if boost:
            self.speed = self.base_speed * 2
        else:
            self.speed = self.base_speed
    
    def set_position(self, x: int, y: int) -> None:
        """Sets the player's position."""
        self.x = x
        self.y = y
    
    def get_position(self) -> tuple[int, int]:
        """Returns the player's position."""
        return (self.x, self.y)
