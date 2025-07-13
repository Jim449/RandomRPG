from unit import Unit

class CombatInput:
    INACTIVE = 0
    MENU = 1
    TARGETING = 2
    MASS_TARGETING = 3
    SPELL_SELECT = 4
    CONFIRMATION = 5
    CLEANUP = 6
    PREPARATION = 7

    COMBAT_FORMATION = {6: [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2)],
                        5: [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)],
                        4: [(0, 0), (2, 0), (0, 1), (1, 1)],
                        3: [(1, 0), (0, 1), (1, 1)],
                        2: [(0, 1), (1, 1)],
                        1: [(1, 0)]}
    
    COMBAT_POSITIONS = [[(80, 128), (208, 128), (336, 128)],
                        [(144, 182), (272, 182)],
                        [(208, 246)]]

    def __init__(self, hero: Unit, enemies: list[Unit]):
        self.hero = hero
        self.enemies = enemies.copy()
        self.units = [hero] + self.enemies
        self.mode_stack = []
        self.mode = self.INACTIVE
        self.enemy_grid = [[None, None, None], [None, None], [None]]
        self.target_x = 0
        self.target_y = 0
        self.menu_options = ["Attack", "Defend", "Cast spell", "Run"]
        self.spell_options = [["", "", "", ""],
                              ["", "", "", ""],
                              ["", "", "", ""],
                              ["", "", "", ""]]
        self.menu_y = 0
        self.submenu_x = 0
        self.submenu_y = 0
        self.confirmation_y = 0
        self.place_enemies(enemies)

    def increase_target_x(self, direction: int) -> bool:
        """Traverses the enemy grid in the given direction RIGHT = 1 or LEFT = -1.
        Returns True if a new enemy is found, False otherwise.
        Uses wrap and skips empty cells."""
        start_x = self.target_x
        self.target_x += direction

        for i in range(3):
            if self.target_x < 0:
                self.target_x = len(self.enemy_grid[self.target_y]) - 1
            elif self.target_x >= len(self.enemy_grid[self.target_y]):
                self.target_x = 0
            
            if self.enemy_grid[self.target_y][self.target_x] is not None:
                return True
            elif self.target_x == start_x:
                return False
            
            self.target_x += direction
        return False

    def increase_target_y(self, direction: int) -> None:
        """Traverses the enemy grid in the given direction DOWN = 1 or UP = -1.
        If direction is 0, current row is searched and search continues DOWN.
        Searches the new row for any enemies, modifying x-value if needed.
        Uses wrap and skips empty cells.
        Guaranteed to find an enemy unless the grid is empty."""

        if direction == 0:
            self.target_y -= 1
            direction = 1
        
        for i in range(3):
            self.target_y += direction
            
            if self.target_y < 0:
                self.target_y = len(self.enemy_grid) - 1
            elif self.target_y >= len(self.enemy_grid):
                self.target_y = 0
            
            if self.target_x >= len(self.enemy_grid[self.target_y]):
                self.target_x = len(self.enemy_grid[self.target_y]) - 1

            if self.enemy_grid[self.target_y][self.target_x] is not None:
                return
            elif self.increase_target_x(1):
                return
    
    def place_enemies(self, opponents: list[Unit]) -> None:
        """Places enemies in the enemy grid based on the number of enemies.
        Sets the pointer to the first enemy."""

        for i, position in enumerate(self.COMBAT_FORMATION[len(opponents)]):
            x = position[0]
            y = position[1]
            self.enemy_grid[y][x] = opponents[i]
            coordinates = self.COMBAT_POSITIONS[y][x]
            opponents[i].set_position(coordinates[0], coordinates[1])
        
        self.target_x = 0
        self.target_y = 0
        self.increase_target_y(0)
    
    def remove_enemy(self, enemy: Unit) -> bool:
        """Removes an enemy from the enemy grid."""
        for row in self.enemy_grid:
            for i, cell in enumerate(row):
                if cell == enemy:
                    row[i] = None
                    break
        try:
            self.enemies.remove(enemy)
            self.units.remove(enemy)
        except ValueError:
            pass
        
        if len(self.enemies) == 0:
            self.mode = self.CLEANUP
            return True
        elif self.get_enemy() is None:
            self.increase_target_y(0)
        return False
    
    def clear_enemies(self) -> None:
        """Clears all enemies from the enemy grid."""
        for y in range(len(self.enemy_grid)):
            for x in range(len(self.enemy_grid[y])):
                self.enemy_grid[y][x] = None
        self.enemies.clear()
    
    def get_enemy(self) -> Unit:
        """Returns the selected enemy."""
        return self.enemy_grid[self.target_y][self.target_x]
    
    def get_enemy_list(self) -> list[Unit]:
        """Returns a list of all enemies."""
        return self.enemies
    
    def get_enemy_count(self) -> int:
        """Returns the number of enemies."""
        return len(self.enemies)
    
    def get_target_pointer(self) -> tuple[int, int]:
        """Returns the target pointer."""
        position = self.get_enemy().get_position()
        return (position[0] + 22, position[1] - 32)
    
    def get_mass_pointers(self) -> list[tuple[int, int]]:
        """Returns targeting pointers for all enemies."""
        pointers = []
        for enemy in self.enemies:
            position = enemy.get_position()
            pointers.append((position[0] + 22, position[1] - 32))
        return pointers
    
    def cycle_menu(self, direction: int) -> None:
        """Cycles the menu in the given direction."""
        self.menu_y += direction
        if self.menu_y < 0:
            self.menu_y = len(self.menu_options) - 1
        elif self.menu_y >= len(self.menu_options):
            self.menu_y = 0

    def get_menu_choice(self) -> str:
        """Returns the menu choice made by the player."""
        return self.menu_options[self.menu_y]
    
    def increase_submenu_x(self, direction: int) -> None:
        """Increases the submenu x in the given direction."""
        self.submenu_x += direction
        if self.submenu_x < 0:
            self.submenu_x = len(self.spell_options[self.submenu_y]) - 1
        elif self.submenu_x >= len(self.spell_options[self.submenu_y]):
            self.submenu_x = 0
    
    def increase_submenu_y(self, direction: int) -> None:
        """Increases the submenu y in the given direction."""
        self.submenu_y += direction
        if self.submenu_y < 0:
            self.submenu_y = len(self.spell_options) - 1
        elif self.submenu_y >= len(self.spell_options):
            self.submenu_y = 0

    def get_spell_choice(self) -> str:
        """Returns the spell choice made by the player."""
        return self.spell_options[self.submenu_y][self.submenu_x]
    
    def set_spells(self, spells: list[str]) -> None:
        """Sets the spells for the combat input."""
        for i in range(16):
            if i < len(spells):
                self.spell_options[i // 4][i % 4] = spells[i]
            else:
                self.spell_options[i // 4][i % 4] = ""
    
    def cycle_confirmation(self, direction: int) -> None:
        """Cycles the confirmation in the given direction."""
        self.confirmation_y += direction
        if self.confirmation_y < 0:
            self.confirmation_y = 1
        elif self.confirmation_y >= 1:
            self.confirmation_y = 0

    def get_confirmation_choice(self) -> bool:
        """Returns the confirmation choice made by the player."""
        if self.confirmation_y == 0:
            return True
        else:
            return False
        
    def set_mode(self, mode: int) -> None:
        """Sets the mode of the combat input."""
        if mode in (self.INACTIVE, self.CLEANUP):
            self.mode_stack.clear()
        else:
            self.mode_stack.append(mode)
        self.mode = mode
    
    def undo_mode(self) -> None:
        """Undoes the last mode change."""
        if len(self.mode_stack) > 1:
            self.mode_stack.pop()
            self.mode = self.mode_stack[-1]
    
    def get_mode(self) -> int:
        """Returns the mode of the combat input."""
        return self.mode
    
    def has_mode(self, mode: int) -> bool:
        """Returns True if the mode is in the mode stack."""
        return mode in self.mode_stack
    
    def increase_x(self, direction: int) -> None:
        """Reacts to a keypress on the x-axis."""
        if self.mode == self.TARGETING:
            self.increase_target_x(direction)
        elif self.mode == self.SPELL_SELECT:
            self.increase_submenu_x(direction)
    
    def increase_y(self, direction: int) -> None:
        """Reacts to a keypress on the y-axis."""
        if self.mode == self.TARGETING:
            self.increase_target_y(direction)
        elif self.mode == self.MENU:
            self.cycle_menu(direction)
        elif self.mode == self.CONFIRMATION:
            self.cycle_confirmation(direction)
        elif self.mode == self.SPELL_SELECT:
            self.increase_submenu_y(direction)
    
    def sort_by_speed(self) -> list[Unit]:
        """Returns a list of characters sorted by speed."""
        sorted = self.units.copy()
        sorted.sort(key=lambda c: c.combat_speed, reverse=True)
        return sorted
    
    def get_first_ready_character(self) -> Unit:
        """Get the first character that is ready to act (has a selected action).
        
        Returns:
            Unit: The first ready character, or None if none are ready"""
        for unit in self.sort_by_speed():
            if unit.can_act():
                print(f"{unit.name} with speed {unit.combat_speed} is ready to act")
                return unit
        return None