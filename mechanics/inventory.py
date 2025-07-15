from mechanics.item import Item
from mechanics.character import Character

class Inventory:
    def __init__(self, coins: int = 0, limit: int = 16):
        self.items: list[Item] = []
        self.coins = coins
        self.limit = limit

    def add_coins(self, amount: int) -> None:
        """Add coins to the inventory"""
        self.coins += amount

    def remove_coins(self, amount: int) -> bool:
        """Remove coins from the inventory"""
        if self.coins < amount:
            return False
        self.coins -= amount
        return True
    
    def add_item(self, item: Item, equip_to: Character = None) -> bool:
        """Add an item to the inventory or increase its amount if it already exists.
        If equip_to is provided, the item is equipped to the character
        but doesn't replace any existing equipment."""
        if len(self.items) < self.limit:
            self.items.append(item)
            if equip_to:
                self.equip(equip_to, item, replace=False)
            return True
        return False
    
    def remove_item(self, index: int) -> bool:
        """
        Remove a specific amount of an item from inventory.
        Returns True if successful, False if item doesn't exist or not enough
        """
        try:
            self.items.pop(index)
            return True
        except IndexError:
            return False
    
    def equip(self, character: Character, item: Item,
              replace: bool = True) -> None:
        """Equip an item to a character.
        If replace is False, the item is only equipped if the character
        doesn't have any equipment of that type."""
        if not item:
            return
        if item.type == Item.WEAPON:
            if replace or not character.weapon:
                character.weapon = item
        elif item.type == Item.ARMOR:
            if replace or not character.armor:
                character.armor = item
        elif item.type == Item.ACCESSORY:
            if replace or not character.accessory:
                character.accessory = item
    
    def get_item(self, index: int) -> Item:
        """Get an item from inventory by index"""
        return self.items[index]
    
    def get_all_items(self) -> list[Item]:
        """Get a list of all items in inventory"""
        return self.items
    
    def __len__(self) -> int:
        """Return the number of unique items"""
        return len(self.items)
    
    def __repr__(self) -> str:
        """String representation of inventory"""
        if not self.items:
            return "Inventory: Empty"
        
        items_str = ", ".join(str(item) for item in self.items)
        return f"Inventory: {items_str}"
