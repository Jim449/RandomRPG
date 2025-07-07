from mechanics.spellEffect import SpellEffect
from typing import Callable, Optional, Any
from random import uniform

DAMAGE_RANGE = (0.8, 1.2)

class Action:
    ACTIVE = "Active"
    PASSIVE = "Passive"
    
    def __init__(self, name: str,
                 action_type: str = ACTIVE,
                 target_ally: bool = False,
                 target_all: bool = False,
                 target_self: bool = False,
                 action_function: Optional[Callable[[Any, Any], str]] = None,
                 effect: Optional[SpellEffect] = None,
                 print_action_name: bool = True):
        """
        Initialize an action.
        
        Args:
            name (str): The name of the action
            effect (SpellEffect, optional): Spell effect to apply after the action
        """
        self.name = name
        self.effect = effect
        self.target_ally = target_ally
        self.target_self = target_self
        self.action_type = action_type
        self.target_all = target_all
        self.action_function = action_function
        self.print_action_name = print_action_name
    
    def set_action_function(self, func: Callable[[Any, Any], str]) -> None:
        """
        Set the function to execute when this action is used.
        
        Args:
            func (Callable[[Character, Character], str]): Function that takes a user Character and a target Character as parameters
        """
        self.action_function = func
    
    def use(self, user: Any, target: Any) -> str:
        """
        Use this action on a target character.
        
        Args:
            user (Character): The character using the action
            target (Character): The character to target
        
        Returns:
            str: The message to display after the action is used
        """
        message = ""
        if self.action_function:
            message = self.action_function(user, target) + "\n"
        
        if self.effect:
            new_effect = self.effect.copy()
            message += target.apply_spell_effect(new_effect)
        
        return message


def attack(user: Any, target: Any) -> str:
    damage = user.get_attack(target)
    damage = round(damage * uniform(*DAMAGE_RANGE))
    target.damage(damage)
    return f"{user.name} attacks {target.name}"

def defend(user: Any, target: Any) -> str:
    return f"{user.name} does nothing"

def inaction(user: Any, target: Any) -> str:
    return f"{user.name} is unable to act"