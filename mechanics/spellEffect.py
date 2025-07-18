from typing import Self, Callable, Any

class SpellEffect:
    def __init__(self, name: str, effect_function: Callable[[Any, int, Any], str], power: int = 1, duration: int = 0, arguments: Any = None):
        """
        Initialize a spell effect.
        
        Args:
            name (str): The name of the spell effect
            duration (int): Duration in turns. 0 means permanent until manually removed.
        """
        self.name = name
        self.power = power
        self.duration = duration
        self.effect_function = effect_function
        self.arguments = arguments

    def copy(self) -> Self:
        """
        Copy this spell effect.
        
        Returns:
            Self: A copy of this spell effect
        """
        return SpellEffect(self.name, self.effect_function,
                           power=self.power, duration=self.duration,
                           arguments=self.arguments)
    
    def can_apply(self, character) -> bool:
        """
        Check if this spell effect can be applied to a character.
        
        Args:
            character (Character): The character to check
        """
        return True
    
    def apply(self, character) -> str:
        """
        Apply this spell effect to a character.
        
        Args:
            character (Character): The character to apply the effect to
        """
        return self.effect_function(character, self.power, self.arguments)
        
    def remove(self, character) -> str:
        """
        Remove this spell effect from a character.
        
        Args:
            character (Character): The character to remove the effect from
        """
        return self.effect_function(character, -self.power, self.arguments)

    
    def tick(self) -> bool:
        """
        Decrease duration by 1 turn.
        
        Returns:
            bool: True if the effect has expired (duration reached 0), False otherwise
        """
        if self.duration > 0:
            self.duration -= 1
            return self.duration == 0
        return False


def increase_stat(character, power, arguments) -> str:
    message = ""
    for stat_name, modifier in arguments.items():
        character.add_temp_modifier(stat_name, modifier * power)
        if stat_name == "Speed":
            character.calculate_speed()
        if power > 0:
            message += f"{character.name} gains {modifier * power} {stat_name}.\n"
    return message


def decrease_stat(character, power, arguments) -> str:
    message = ""
    for stat_name, modifier in arguments.items():
        character.add_temp_modifier(stat_name, modifier * -power)
        if stat_name == "Speed":
            character.calculate_speed()
        if power > 0:
            message += f"{character.name} loses {modifier * power} {stat_name}.\n"
    return message