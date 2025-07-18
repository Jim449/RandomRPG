import pygame
from mechanics.character import Character
from conversation import Conversation
from encounter import Encounter

class Presence:
    """An object on the map that can be interacted with
    or trigger an encounter.
    A presence can be a visible npc or object,
    or a hidden trigger."""
    def __init__(self, grid_x: int = -1, grid_y: int = -1,
                 sprite: pygame.Surface = None,
                 blink_sprite: pygame.Surface = None,
                 encounter: Encounter = None,
                 trigger_on_contact: bool = False):
        self.grid_x: int = grid_x
        self.grid_y: int = grid_y
        self.sprite: pygame.Surface = sprite
        self.blink_sprite: pygame.Surface = blink_sprite
        self.encounter: Encounter = encounter
        self.trigger_on_contact: bool = trigger_on_contact
        self.x: int = grid_x * 32
        self.y: int = grid_y * 32
        self.alpha: int = 255
        self.flashing: bool = False
        self.conversations: list[Conversation] = []
    
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
    
    def get_sprite(self) -> pygame.Surface:
        """Returns the unit's sprite."""
        if self.flashing:
            return self.blink_sprite
        else:
            return self.sprite
    
    def add_conversation(self, conversation: Conversation) -> None:
        """Adds a conversation to the unit."""
        self.conversations.append(conversation)


class Unit(Character, Presence):
    """A character capable of moving around the map
    or participate in combat."""
    def __init__(self, name: str, sprite: pygame.Surface,
                 team: int = 1, grid_x: int = 0, grid_y: int = 0,
                 level: int = 1,
                 blink_sprite: pygame.Surface = None):
        Character.__init__(self, name=name, team=team, level=level)
        Presence.__init__(self, grid_x=grid_x, grid_y=grid_y, sprite=sprite, blink_sprite=blink_sprite)
        self.moving: bool = False
        self.direction: tuple[int, int] = (0, 0)
        self.x_offset: int = 0
        self.y_offset: int = 0
        self.base_speed: int = 2
        self.adventure_speed: int = 2
        self.speed_boost: bool = False
    
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
    
    def set_speed_boost(self, boost: bool) -> None:
        """Enable or disable speed boost (double speed when P is held)"""
        self.speed_boost = boost
        if boost:
            self.adventure_speed = self.base_speed * 2
        else:
            self.adventure_speed = self.base_speed