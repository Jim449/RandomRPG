from unit import Unit
from mechanics.inventory import Inventory
from mechanics.item import Item

class AdventureMenu:
    INACTIVE = 0
    MENU = 1
    SPELLBOOK = 2
    INVENTORY = 3
    CONFIRMATION = 4
    ITEM_DETAILS = 5
    SPELL_DETAILS = 6
    SAVE = 7
    LOAD = 8
    QUIT = 9
    STATUS = 10
    EQUIPMENT = 11

    def __init__(self, player: Unit, inventory: Inventory):
        self.player = player
        self.inventory = inventory
        self.mode = AdventureMenu.INACTIVE
        self.mode_stack = [AdventureMenu.INACTIVE]
        self.menu_options = [["Status", "Equipment"], ["Inventory", "Spellbook"], ["Save", "Load"], ["Exit menu", "Quit game"]]
        self.item_options = ["Equip", "Use", "Discard", "Cancel"]
        self.equipment_options = ["Inventory", "Unequip", "Cancel"]
        self.spell_options = ["Cast", "Cancel"]
        self.items = [["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]]
        self.spells = [["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]]
        self.equipment = ["", "", "", "Cancel"]
        self.menu_x = 0
        self.menu_y = 0
        self.submenu_x = 0
        self.submenu_y = 0
        self.details_y = 0
        self.confirmation_y = 0
    
    def get_mode(self) -> int:
        return self.mode
    
    def set_mode(self, mode: int) -> None:
        """Sets the mode of the adventure menu."""
        if mode == self.INACTIVE:
            self.mode_stack.clear()
        self.mode_stack.append(mode)
        self.mode = mode
    
    def undo_mode(self) -> None:
        """Undoes the last mode change."""
        if len(self.mode_stack) > 1:
            self.mode_stack.pop()
            self.mode = self.mode_stack[-1]
    
    def is_active(self) -> bool:
        """Returns True if the adventure menu is active."""
        return self.mode != self.INACTIVE
    
    def has_mode(self, mode: int) -> bool:
        """Returns True if the mode is in the mode stack."""
        return mode in self.mode_stack
    
    def open_inventory(self) -> None:
        """Opens the inventory menu."""
        self.set_mode(self.INVENTORY)

        for i in range(12):
            x = i % 3
            y = i // 3
            if i < len(self.inventory.items):
                self.items[y][x] = self.inventory.items[i]
            else:
                self.items[y][x] = ""
    
    def load_equipment(self) -> None:
        """Loads the equipment into the menu."""
        if self.player.weapon:
            self.equipment[0] = self.player.weapon.name
        else:
            self.equipment[0] = ""
        if self.player.armor:
            self.equipment[1] = self.player.armor.name
        else:
            self.equipment[1] = ""
        if self.player.accessory:
            self.equipment[2] = self.player.accessory.name
        else:
            self.equipment[2] = ""
    
    def get_menu_choice(self) -> str:
        """Returns the choice of the menu."""
        return self.menu_options[self.menu_y][self.menu_x]
    
    def get_selected_item(self) -> Item:
        """Returns the selected item."""
        return self.items[self.submenu_y][self.submenu_x]
    
    def get_item_choice(self) -> str:
        """Returns the action to take with the item."""
        return self.item_options[self.details_y]

    def get_equipment_selection(self) -> str:
        """Returns the selected equipment type."""
        if self.submenu_y == 0:
            return "Weapon"
        elif self.submenu_y == 1:
            return "Armor"
        elif self.submenu_y == 2:
            return "Accessory"
        else:
            return "Cancel"
    
    def get_equipment_choice(self) -> str:
        """Returns the action to take with the equipment."""
        return self.equipment_options[self.details_y]
    
    def get_equipment_info(self) -> list[str]:
        """Returns the equipment and coin amount."""
        equipment = self.equipment[:3]
        equipment.append(f"{self.inventory.coins}s")
        return equipment
    
    def increase_menu_x(self, direction: int) -> None:
        self.menu_x = (self.menu_x + direction) % len(self.menu_options[self.menu_y])
    
    def increase_menu_y(self, direction: int) -> None:
        self.menu_y = (self.menu_y + direction) % len(self.menu_options)

    def increase_submenu_x(self, direction: int) -> None:
        self.submenu_x = (self.submenu_x + direction) % len(self.items[self.submenu_y])
    
    def increase_submenu_y(self, direction: int) -> None:
        self.submenu_y = (self.submenu_y + direction) % len(self.items)

    def increase_details_y(self, direction: int) -> None:
        self.details_y = (self.details_y + direction) % len(self.item_options)
    
    def increase_confirmation_y(self) -> None:
        if self.confirmation_y == 0:
            self.confirmation_y = 1
        else:
            self.confirmation_y = 0

    def increase_x(self, direction: int) -> None:
        """Increases the x position of the menu."""
        if self.mode == self.MENU:
            self.increase_menu_x(direction)
        elif self.mode == self.INVENTORY:
            self.increase_submenu_x(direction)

    def increase_y(self, direction: int) -> None:
        """Increases the y position of the current menu."""
        if self.mode == self.MENU:
            self.increase_menu_y(direction)
        elif self.mode in (self.INVENTORY, self.SPELLBOOK):
            self.increase_submenu_y(direction)
        elif self.mode in (self.ITEM_DETAILS, self.SPELL_DETAILS):
            self.increase_details_y(direction)
        elif self.mode == self.CONFIRMATION:
            self.increase_confirmation_y()