from typing import Dict, List, Optional
from mechanics.item import Item
from mechanics.character import Character

class Inventory:
    def __init__(self, coins: int = 0):
        self.items: Dict[str, Item] = {}
        self.coins = coins

    def add_coins(self, amount: int) -> None:
        """Add coins to the inventory"""
        self.coins += amount

    def remove_coins(self, amount: int) -> bool:
        """Remove coins from the inventory"""
        if self.coins < amount:
            return False
        self.coins -= amount
        return True
    
    def add_item(self, item: Item) -> None:
        """Add an item to the inventory or increase its amount if it already exists."""
        if item.name in self.items:
            self.items[item.name].amount += item.amount
        else:
            self.items[item.name] = item
    
    def remove_item(self, item_name: str, amount: int = 1) -> bool:
        """
        Remove a specific amount of an item from inventory.
        Returns True if successful, False if item doesn't exist or not enough
        """
        if item_name not in self.items:
            return False
        
        if self.items[item_name].amount < amount:
            return False
        
        self.items[item_name].amount -= amount
        
        if self.items[item_name].amount == 0:
            del self.items[item_name]
            
        return True
    
    def equip_to_character(self, character: Character, item: Item) -> None:
        """Equip an item to a character"""
        if item.type == Item.WEAPON:
            if character.weapon:
                self.unequip_item(character.weapon)
            character.weapon = item
        elif item.type == Item.ARMOR:
            if character.armor:
                self.unequip_item(character.armor)
            character.armor = item
        elif item.type == Item.ACCESSORY:
            if character.accessory:
                self.unequip_item(character.accessory)
            character.accessory = item
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Get an item from inventory by name"""
        return self.items.get(item_name)
    
    def has_item(self, item_name: str, amount: int = 1) -> bool:
        """Check if inventory has at least specified amount of an item"""
        if item_name not in self.items:
            return False
        return self.items[item_name].amount >= amount
    
    def get_all_items(self) -> List[Item]:
        """Get a list of all items in inventory"""
        return list(self.items.values())
    
    def __len__(self) -> int:
        """Return the number of unique items"""
        return len(self.items)
    
    def __repr__(self) -> str:
        """String representation of inventory"""
        if not self.items:
            return "Inventory: Empty"
        
        items_str = ", ".join(str(item) for item in self.items.values())
        return f"Inventory: {items_str}"
