from mechanics.spellEffect import SpellEffect
from typing import Callable, Optional, Any, Self
from random import uniform

DAMAGE_RANGE = (0.8, 1.2)

class Action:
    ACTIVE = "Active"
    PASSIVE = "Passive"
    BASE_AMOUNT = "base_amount"
    SPELL_POWER = "spell_power"
    TARGET_VITALITY = "target_vitality"
    
    def __init__(self, name: str,
                 action_type: str = ACTIVE,
                 target_ally: bool = False,
                 target_all: bool = False,
                 target_self: bool = False,
                 action_function: Optional[Callable[[Any, Any], str]] = None,
                 effect: Optional[SpellEffect] = None,
                 print_action_name: bool = True,
                 arguments: dict = None):
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
        self.arguments = arguments
    
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
            message = self.action_function(user, target, self.arguments) + "\n"
        
        if self.effect:
            new_effect = self.effect.copy()
            message += target.apply_spell_effect(new_effect)
        
        return message
    
    def copy(self, override_arguments: dict = None) -> Self:
        if override_arguments:
            arguments = override_arguments
        else:
            arguments = self.arguments

        return Action(name=self.name,
                      action_type=self.action_type,
                      target_ally=self.target_ally, 
                      target_all=self.target_all,
                      target_self=self.target_self,
                      action_function=self.action_function,
                      effect=self.effect,
                      print_action_name=self.print_action_name,
                      arguments=arguments)


def attack(user: Any, target: Any, arguments: Any = None) -> str:
    damage = user.get_attack(target)
    damage = round(damage * uniform(*DAMAGE_RANGE))
    target.damage(damage)
    return f"{user.name} attacks {target.name}"

def defend(user: Any, target: Any, arguments: Any = None) -> str:
    return f"{user.name} does nothing"

def inaction(user: Any, target: Any, arguments: Any = None) -> str:
    return f"{user.name} is unable to act"

def heal(user: Any, target: Any, arguments: Any = None) -> str:
    amount = 0

    if Action.BASE_AMOUNT in arguments:
        amount = arguments[Action.BASE_AMOUNT] * (1 + user.level * 0.2)
    if Action.SPELL_POWER in arguments:
        amount += user.get_final_stat("Resistance") * arguments[Action.SPELL_POWER] * (1 + user.level * 0.2) 
    if Action.TARGET_VITALITY in arguments:
        amount += target.get_final_stat("Stamina") * arguments[Action.TARGET_VITALITY] * (1 + target.level * 0.2)
    amount = round(amount * uniform(*DAMAGE_RANGE))
    
    healing = target.full_heal(amount)
    return f"{target.name} recovers {healing} HP"