from unit import Unit

class CombatInput:
    INACTIVE = 0
    MENU = 1
    TARGETING = 2
    MASS_TARGETING = 3
    SPELL_SELECT = 4
    CONFIRMATION = 5
    CLEANUP = 6

    def __init__(self):
        self.mode_stack = []
        self.mode = self.INACTIVE
        self.enemy_grid = [[(80, 128), (208, 128), (336, 128)], [(144, 172), (272, 172)], [(208, 236)]]
        self.enemies = [[None, None, None], [None, None], [None]]
        self.enemy_count = 0
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

        self.COMBAT_POSITIONS = {6: [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2)],
                                 5: [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)],
                                 4: [(0, 0), (2, 0), (0, 1), (1, 1)],
                                 3: [(1, 0), (0, 1), (1, 1)],
                                 2: [(0, 1), (1, 1)],
                                 1: [(1, 0)]}

        # This leaves me with 15x5 free cells at the bottom of the screen
        # But realistically, I can only use 15x4
        # Which translates to 480x128px

    def increase_target_x(self, direction: int) -> bool:
        """Traverses the enemy grid in the given direction RIGHT = 1 or LEFT = -1.
        Returns True if a new enemy is found, False otherwise.
        Uses wrap and skips empty cells."""
        start_x = self.target_x
        self.target_x += direction

        while self.target_x != start_x:
            if self.target_x < 0:
                self.target_x = len(self.enemies[self.target_y]) - 1
            elif self.target_x >= len(self.enemies[self.target_y]):
                self.target_x = 0
            
            if self.enemies[self.target_y][self.target_x] is not None:
                return True
            
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
        
        while True:
            self.target_y += direction
            
            if self.target_y < 0:
                self.target_y = len(self.enemies) - 1
            elif self.target_y >= len(self.enemies):
                self.target_y = 0
            
            if self.target_x >= len(self.enemies[self.target_y]):
                self.target_x = len(self.enemies[self.target_y]) - 1

            if self.enemies[self.target_y][self.target_x] is not None:
                return
            elif self.increase_target_x(1):
                return
    
    def place_enemies(self, opponents: list[Unit]) -> None:
        """Places enemies in the enemy grid based on the number of enemies.
        Sets the pointer to the first enemy."""
        self.enemy_count = len(opponents)

        for i, position in enumerate(self.COMBAT_POSITIONS[self.enemy_count]):
            x = position[0]
            y = position[1]
            opponents[i].set_position(x, y)
            self.enemies[y][x] = opponents[i]
        
        self.target_x = 0
        self.target_y = 0
        self.increase_target_y(0)
    
    def remove_enemy(self, enemy: Unit) -> bool:
        """Removes an enemy from the enemy grid."""
        self.enemies[enemy.y][enemy.x] = None
        self.enemy_count -= 1
        if self.enemy_count == 0:
            self.mode = self.CLEANUP
            return True
        elif self.get_enemy() is None:
            self.increase_target_y(0)
        return False
    
    def clear_enemies(self) -> None:
        """Clears all enemies from the enemy grid."""
        for y in range(len(self.enemies)):
            for x in range(len(self.enemies[y])):
                self.enemies[y][x] = None
    
    def get_enemy(self) -> Unit:
        """Returns the selected enemy."""
        return self.enemies[self.target_y][self.target_x]
    
    def get_enemy_list(self) -> list[Unit]:
        """Returns a list of all enemies."""
        enemies = []
        for y in range(len(self.enemies)):
            for x in range(len(self.enemies[y])):
                if self.enemies[y][x] is not None:
                    enemies.append(self.enemies[y][x])
        return enemies
    
    def get_target_pointer(self) -> tuple[int, int]:
        """Returns the target pointer."""
        position = self.enemy_grid[self.target_y][self.target_x]
        return (position[0] + 16, position[1] - 32)
    
    def get_mass_pointers(self) -> list[tuple[int, int]]:
        """Returns targeting pointers for all enemies."""
        pointers = []
        for y in range(len(self.enemy_grid)):
            for x in range(len(self.enemy_grid[y])):
                if self.enemy_grid[y][x] is not None:
                    position = self.enemy_grid[y][x]
                    pointers.append((position[0] + 16, position[1] - 32))
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
        if self.mode_stack:
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
    