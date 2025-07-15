from unit import Unit
from combat_input import CombatInput
from random import randrange
from mechanics.storage import Storage

class Combat:
    """Controls combat flow."""
    PHASE_DECIDE_ACTION = 0
    PHASE_USE_ACTION = 1
    PHASE_END_ROUND = 2
    PHASE_NEXT_ROUND = 3
    PHASE_VICTORY = 4
    PHASE_DEFEAT = 5
    PHASE_INACTIVE = 6
    PHASE_VOID = 7

    def __init__(self, combat_input: CombatInput):
        self.combat_input = combat_input
        self.round = 0
        self.phase = self.PHASE_DECIDE_ACTION
        self.message = ""
        self.active_unit = None
        self.current_targets = []
        self.defeated_units = []
        
        for unit in self.combat_input.units:
            unit.start_combat()
    
    def end_combat(self) -> None:
        """End the combat."""
        pass

    def check_combat_end(self) -> bool:
        """Check if the combat should end.
        
        Returns:
            bool: True if combat should end, False otherwise"""
        if self.combat_input.hero.defeated:
            self.phase = self.PHASE_DEFEAT
            print("Combat defeat")
            return True
        elif self.combat_input.get_enemy_count() == 0:
            self.phase = self.PHASE_VICTORY
            print("Combat victory")
            return True
        else:
            return False
    
    def find_defeated_units(self) -> list[Unit]:
        """Finds all defeated units."""
        self.defeated_units = []
        for unit in self.combat_input.units:
            if unit.defeated:
                self.defeated_units.append(unit)
        return self.defeated_units
    
    def has_defeated_units(self) -> bool:
        """Checks if there are any defeated units."""
        return len(self.defeated_units) > 0
    
    def remove_defeated_units(self) -> None:
        """Removes defeated units."""
        for unit in self.defeated_units:
            self.combat_input.remove_enemy(unit)
        self.defeated_units = []
        self.check_combat_end()
    
    def remove_unit(self, unit: Unit) -> None:
        """Removes a unit."""
        self.combat_input.remove_enemy(unit)
        self.defeated_units.remove(unit)
        self.check_combat_end()
    
    def select_action(self, action, target: Unit) -> None:
        """Selects an action for a player controlled unit."""
        self.combat_input.hero.select_action(action, target)
        self.phase = self.PHASE_USE_ACTION

    def decide_action(self, unit: Unit) -> None:
        """Decides an action for an enemy unit."""
        options = unit.moveset.copy()

        while len(options) > 0:
            choice = randrange(len(options))
            action = options[choice]
            options.remove(action)

            # TODO: need to check if spell effect can be applied to target
            # without overwriting existing effects
            # Otherwise, try another action
            # Need a skip/defend action
            if not action.target_ally:
                unit.select_action(action, self.combat_input.hero)
            elif action.target_self:
                unit.select_action(action, unit)
            elif action.target_all:
                unit.select_action(action, self.combat_input.enemies)
            else:
                target_choice = randrange(len(self.combat_input.enemies))
                target = self.combat_input.enemies[target_choice]
                unit.select_action(action, target)
            return

    def decide_all_actions(self) -> None:
        """Decides actions for all units."""
        self.combat_input.hero.clear_selection()
        # Maybe I should let the player select an action anyways
        # It could be a "wake-up" action that works when the hero is stunned
        if self.combat_input.hero.can_select_action():
            self.combat_input.set_mode(CombatInput.MENU)
            
        for enemy in self.combat_input.enemies:
            if enemy.can_select_action():
                self.decide_action(enemy)

    def use_next_action(self) -> bool:
        """Uses the next action.
        
        Returns:
            bool: True if an action was used, False if noone was able to act"""
        character = self.combat_input.get_first_ready_character()
        if character:
            self.active_unit = character
            if not character.can_act():
                action = Storage.get_action("Inaction")
                character.select_action(action, character)
                self.message = character.use_selected_action()
                self.current_targets = [character]
            if character.target_all:
                # Assuming all mass actions target all enemies
                # There's only one hero after all
                self.message = character.use_action_on_all(self.combat_input.enemies)
                self.current_targets = self.combat_input.enemies
            else:
                self.message = character.use_selected_action()
                print("Action message: " + self.message)
                print(f"Inflicted {-character.target.health_change} damage. Defender has {character.target.get_final_stat("Health")} health remaining.")
                self.current_targets = [character.target]
            self.find_defeated_units()
            return True
        else:
            return False
    
    def end_round(self) -> None:
        """Ticks effects for all units."""
        for character in self.combat_input.units:
            character.end_round()
        self.current_targets = self.combat_input.units
        self.find_defeated_units()
        
    def process_turn(self) -> bool:
        """Process a single turn of combat.
        
        Returns:
            bool: True if combat continues, False if combat should end"""
        if self.check_combat_end():
            return False
        
        if self.phase == self.PHASE_DECIDE_ACTION:
            self.decide_all_actions()
            print("Deciding actions")
            return True
        elif self.phase == self.PHASE_USE_ACTION:
            if not self.use_next_action():
                self.clear_targeting()
                self.phase = self.PHASE_END_ROUND
            return True
        elif self.phase == self.PHASE_END_ROUND:
            print("Ending round")
            self.end_round()
            self.phase = self.PHASE_NEXT_ROUND
            return True
        elif self.phase == self.PHASE_NEXT_ROUND:
            print("Next round")
            self.round += 1
            for character in self.combat_input.units:
                character.start_round()
            self.phase = self.PHASE_DECIDE_ACTION
            return True
        return True

    def next_phase(self) -> None:
        """Moves to the next phase."""
        # After the player has decided his action,
        # I need to move to the next phase
        # Other phase transitions happens in process_turn
        if self.phase == self.PHASE_DECIDE_ACTION:
            self.phase = self.PHASE_USE_ACTION
    
    def clear_targeting(self) -> None:
        """Clears active unit and targets."""
        self.active_unit = None
        self.current_targets = []