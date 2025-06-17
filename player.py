import pygame

class Player():
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.moving: bool = False
        self.direction: tuple[int, int] = (0, 0)
        self.x_offset: int = 0
        self.y_offset: int = 0
        self.base_speed: int = 2
        self.speed: int = 2
        self.speed_boost: bool = False
        self.sprite: pygame.Surface = pygame.image.load("resources/people/player_small.png")
    
    def move(self) -> None:
        if not self.moving:
            return
        
        self.x_offset += self.direction[0] * self.speed
        self.y_offset += self.direction[1] * self.speed
        
        if abs(self.x_offset) == 32 or abs(self.y_offset) == 32:
            self.x += self.direction[0]
            self.y += self.direction[1]
            self.x_offset = 0
            self.y_offset = 0
            self.moving = False
            
    def start_movement(self, direction: tuple[int, int]) -> bool:
        if self.moving:
            return False
        else:
            self.moving = True
            self.direction = direction
            self.move()
    
    def set_speed_boost(self, boost: bool) -> None:
        """Enable or disable speed boost (double speed when P is held)"""
        self.speed_boost = boost
        if boost:
            self.speed = self.base_speed * 2
        else:
            self.speed = self.base_speed
