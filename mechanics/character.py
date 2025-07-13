from mechanics.characterStats import CharacterStats
from mechanics.spellEffect import SpellEffect
from mechanics.action import Action
from mechanics.item import Item
from typing import List, Optional, Self
from random import random
from math import floor

class Character:
    LEVEL_BONUS = 0.2
    LEVEL_CAP = 20
    EXPERIENCE_REQUIREMENT = (0, 100, 400, 900, 1600,
                              2500, 3600, 4900, 8100,
                              10000, 12100, 14400, 16900,
                              19600, 22500, 25600, 28900,
                              32400, 36100, 40000)
    STRENGTH = "Strength"
    DEFENSE = "Defense"
    INTELLIGENCE = "Intelligence"
    RESISTANCE = "Resistance"
    AGILITY = "Agility"
    STAMINA = "Stamina"
    HP = "Health"
    MP = "Magic"
    MAX_HP = "MaxHealth"
    MAX_MP = "MaxMagic"
    FULL_HP = "FullHealth"
    FULL_MP = "FullMagic"
    RANK = "Rank"
    CONSTITUTION = "Constitution"
    
    def __init__(self, name: str, team: int = 1, level: int = 1):
        self.name = name
        self.team = team
        self.level = level
        self.experience = self.EXPERIENCE_REQUIREMENT[level - 1]
        self.base_stats = CharacterStats()
        self.temp_modifiers = CharacterStats()
        self.active_effects = []
        self.moveset: List[Action] = []
        self.weapon: Optional[Item] = None
        self.armor: Optional[Item] = None
        self.accessory: Optional[Item] = None
        self.selected_action: Optional[Action] = None
        self.target: Optional[Character] = None
        self.target_all = False
        self.action_points = 0
        self.max_action_points = 1
        self.combat_speed = 0.0
        self.health_change = 0
        self.display_health = 0
        self.stunned = False
        self.silenced = False
        self.defeated = False
    
    def set_base_stat(self, stat_name: str, value: int) -> None:
        """Set a base stat value."""
        self.base_stats.set_stat(stat_name, value)
    
    def get_base_stat(self, stat_name: str) -> int:
        """Get a base stat value."""
        return self.base_stats.get_stat(stat_name)
    
    def add_temp_modifier(self, stat_name: str, modifier: int) -> None:
        """Add a temporary modifier to a stat."""
        self.temp_modifiers.modify_stat(stat_name, modifier)
    
    def remove_temp_modifier(self, stat_name: str) -> None:
        """Remove a temporary modifier from a stat."""
        self.temp_modifiers.remove_stat(stat_name)
    
    def get_final_stat(self, stat_name: str) -> int:
        """Calculate the final stat value including temporary modifiers."""
        base_value = self.get_base_stat(stat_name)
        temp_mod = self.temp_modifiers.get_stat(stat_name)
        return base_value + temp_mod
    
    def get_attack(self, opponent: Self) -> float:
        """Calculates the attack value."""
        value = self.get_final_stat(self.STRENGTH)
        if self.weapon:
            value += self.weapon.strength
        if self.armor:
            value += self.armor.strength
        if self.accessory:
            value += self.accessory.strength
        value -= opponent.get_defense()
        bonus = 1 + self.level * self.LEVEL_BONUS
        value *= bonus
        return max(0, value)
            
    def get_defense(self) -> int:
        """Calculates the defense value."""
        value = self.get_final_stat(self.DEFENSE)
        if self.weapon:
            value += self.weapon.defense
        if self.armor:
            value += self.armor.defense
        if self.accessory:
            value += self.accessory.defense
        return value
    
    def get_magic_attack(self, opponent: Self, power: int = 0) -> float:
        """Calculates the magic attack value."""
        value = self.get_final_stat(self.INTELLIGENCE)
        if self.weapon:
            value += self.weapon.intelligence
        if self.armor:
            value += self.armor.intelligence
        if self.accessory:
            value += self.accessory.intelligence
        value -= opponent.get_resistance()
        bonus = 1 + self.level * self.LEVEL_BONUS
        value *= bonus
        return max(0, value)

    def get_resistance(self) -> int:
        """Calculate the resistance value."""
        value = self.get_final_stat(self.RESISTANCE)
        if self.weapon:
            value += self.weapon.resistance
        if self.armor:
            value += self.armor.resistance
        if self.accessory:
            value += self.accessory.resistance
        return value
    
    def get_agility(self) -> int:
        """Calculate the agility value."""
        value = self.get_final_stat(self.AGILITY)
        if self.weapon:
            value += self.weapon.agility
        if self.armor:
            value += self.armor.agility
        if self.accessory:
            value += self.accessory.agility
        return value
    
    def calculate_health(self) -> None:
        """Sets the full health value."""
        value = floor(self.get_base_stat(self.RANK) * self.get_base_stat(self.CONSTITUTION) \
                      * (1 + self.level * self.LEVEL_BONUS))
        self.base_stats.set_stat(self.FULL_HP, value)
    
    def calculate_magic(self) -> None:
        """Sets the full magic value."""
        value = floor(self.get_final_stat(self.INTELLIGENCE) * (1 + self.level * self.LEVEL_BONUS))
        self.base_stats.set_stat(self.FULL_MP, value)
    
    def set_stats(self, stats: CharacterStats) -> None:
        """Sets the character's stats."""
        self.base_stats = stats
        self.calculate_health()
        self.calculate_magic()
        self.full_heal()
        self.full_restore()

    def get_experience(self) -> int:
        """Returns the experience reward for defeating the character."""
        return int((self.get_base_stat(self.RANK)**2
                    * self.get_base_stat(self.CONSTITUTION)
                    * (1 + self.level * self.LEVEL_BONUS)) / 4)
    
    def set_actions(self, actions: List[Action]) -> None:
        """Sets the character's actions."""
        self.moveset = actions
    
    def get_all_final_stats(self) -> dict:
        """Get all final stats as a dictionary."""
        final_stats = {}
        # Get all unique stat names from both base and temp modifiers
        all_stats = set(self.base_stats.get_all_stats().keys()) | set(self.temp_modifiers.get_all_stats().keys())
        
        for stat_name in all_stats:
            final_stats[stat_name] = self.get_final_stat(stat_name)
        
        return final_stats
    
    def clear_temp_modifiers(self) -> None:
        """Remove all temporary modifiers."""
        self.temp_modifiers.clear_stats()
    
    def apply_spell_effect(self, effect: SpellEffect) -> str:
        """
        Apply a spell effect to the character.
        
        Args:
            effect (SpellEffect): The spell effect to apply
        """
        message = effect.apply(self)
        self.active_effects.append(effect)
        return message
    
    def remove_spell_effect(self, effect: SpellEffect) -> str:
        """
        Remove a spell effect from the character.
        
        Args:
            effect (SpellEffect): The spell effect to remove
        """
        message = ""

        if effect in self.active_effects:
            effect.remove(self)
            self.active_effects.remove(effect)
            message += f"{self.name} is no longer affected by {effect.name}.\n"
        return message
    
    def tick_spell_effects(self) -> None:
        """
        Decrease duration of all active spell effects by 1 turn.
        Remove any effects that have expired.
        """
        message = ""

        effects_to_remove = []
        for effect in self.active_effects:
            if effect.tick():
                effects_to_remove.append(effect)
        
        # Remove expired effects
        for effect in effects_to_remove:
            message += self.remove_spell_effect(effect)
        return message
    
    def get_active_effects(self) -> list:
        """
        Get a list of all active spell effects.
        
        Returns:
            list: List of active SpellEffect objects
        """
        return self.active_effects.copy()
    
    def clear_all_effects(self) -> None:
        """
        Remove all active spell effects from the character.
        """
        message = ""

        for effect in self.active_effects.copy():
            message += self.remove_spell_effect(effect)    
        return message
    
    def add_action(self, action: Action) -> None:
        """
        Add an action to the character's moveset.
        
        Args:
            action (Action): The action to add
        """
        self.moveset.append(action)
    
    def remove_action(self, action: Action) -> None:
        """
        Remove an action from the character's moveset.
        
        Args:
            action (Action): The action to remove
        """
        if action in self.moveset:
            self.moveset.remove(action)
    
    def select_action(self, action: Action, target: Self,
                      target_all: bool = False) -> bool:
        """
        Select an action and target to use.
        
        Args:
            action (Action): The action to select
            target (Character): The target character
            
        Returns:
            bool: True if selection was successful, False otherwise
        """
        self.selected_action = action
        self.target = target
        self.target_all = target_all
        return True

    def clear_selection(self) -> None:
        """Clear the currently selected action and target."""
        self.selected_action = None
        self.target = None
        self.target_all = False
    
    def use_selected_action(self) -> str:
        """
        Use the currently selected action on the selected target.
        
        Returns:
            str: The message to display after the action is used
        """
        if self.selected_action.print_action_name:
            message = f"{self.name} uses {self.selected_action.name}\n"
        else:
            message = ""
        message += self.selected_action.use(self, self.target)
        self.action_points -= 1
        return message
    
    def use_action_on_all(self, targets: List[Self]) -> str:
        """
        Use the currently selected action on all targets.
        
        Returns:
            str: The message to display after the action is used
        """
        message = f"{self.name} uses {self.selected_action.name}.\n"
        for target in targets:
            message += self.selected_action.use(self, target)
        self.action_points -= 1
        self.clear_selection()
        return message
    
    def can_select_action(self) -> bool:
        """
        Check if the character can select an action.
        
        Returns:
            bool: True if character can select an action
        """
        return (not self.defeated and
                self.action_points > 0 and 
                not self.selected_action)
    
    def can_act(self) -> bool:
        """
        Check if the character can perform an action.
        
        Returns:
            bool: True if character can act
        """
        return (not self.defeated and
                self.action_points > 0 and 
                self.selected_action is not None and
                ((self.target and not self.target.defeated)
                 or self.target_all))
    
    def start_combat(self) -> str:
        """Activates passive effects at the start of combat.
        Rolls speed and sets action points."""
        message = ""
        if self.weapon and self.weapon.has_passive():
            message += self.weapon.action.use(self, self)
        if self.armor and self.armor.has_passive():
            message += self.armor.action.use(self, self)
        if self.accessory and self.accessory.has_passive():
            message += self.accessory.action.use(self, self)
        self.calculate_speed()
        self.action_points = self.max_action_points
        self.display_health = self.base_stats.get_stat(self.HP)
        return message

    def start_round(self) -> None:
        """Reset character state at the start of their turn."""
        self.action_points = self.max_action_points
    
    def end_round(self) -> str:
        """Clean up character state at the end of their turn."""
        self.clear_selection()
        return self.tick_spell_effects()
        
    def get_allied_team(self) -> int:
        """Get the allied team of the character."""
        return self.team
    
    def get_opponent_team(self) -> int:
        """Get the opponent team of the character."""
        return (self.team + 1) % 2
    
    def damage(self, amount: int) -> None:
        """Damage the character."""
        self.health_change = -self.base_stats.deplete_stat(self.HP, amount)
        if self.base_stats.get_stat(self.HP) <= 0:
            self.defeated = True
    
    def heal(self, amount: int) -> None:
        """Heal the character."""
        self.health_change = self.base_stats.restore_stat(self.HP, self.MAX_HP, amount)
    
    def full_heal(self) -> None:
        """Fully heals the character."""
        self.base_stats.restore_stat(self.MAX_HP, self.FULL_HP, 1000)
        self.heal(1000)
    
    def restore(self, amount: int) -> None:
        """Restores magical energy."""
        self.base_stats.restore_stat(self.MP, self.MAX_MP, amount)
    
    def full_restore(self) -> None:
        """Fully restores magical energy."""
        self.base_stats.restore_stat(self.MAX_MP, self.FULL_MP, 1000)
        self.restore(1000)
    
    def calculate_speed(self) -> None:
        """Calculate the speed of the character."""
        self.combat_speed = self.get_agility() + self.level * self.LEVEL_BONUS + random()

    def gain_experience(self, amount: int) -> bool:
        """Gain experience.
        Returns True if the character leveled up, False otherwise."""
        if self.level >= self.LEVEL_CAP:
            return False
        
        self.experience += amount

        if self.experience < self.EXPERIENCE_REQUIREMENT[self.level]:
            return False

        while self.experience >= self.EXPERIENCE_REQUIREMENT[self.level]:
            self.level += 1
            self.calculate_health()
            self.calculate_magic()
            if self.level == self.LEVEL_CAP:
                self.experience = self.EXPERIENCE_REQUIREMENT[self.level - 1]
                return True
        return True

    def present(self) -> str:
        """Present the character in a string."""
        text = f"{self.name} ({self.base_stats.get_stat(self.HP)}/{self.base_stats.get_stat(self.MAX_HP)})"
        for effect in self.active_effects:
            text += f"\n{effect.name} ({effect.duration} turns left)"
        return text
