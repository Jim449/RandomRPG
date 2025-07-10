from mechanics.action import Action

class Item:
    WEAPON = "Weapon"
    ACCESSORY = "Accessory"
    ARMOR = "Armor"
    CONSUMABLE = "Consumable"
    MISC = "Misc"

    def __init__(self, name: str, description: str, amount: int = 1, 
                 type: str = MISC, action: Action = None,
                 strength: int = 0, intelligence: int = 0,
                 defense: int = 0, resistance: int = 0,
                 agility: int = 0, stamina: int = 0):
        self.name = name
        self.type = type
        self.description = description
        self.amount = amount
        self.action = action
        self.strength = strength
        self.intelligence = intelligence
        self.defense = defense
        self.resistance = resistance
        self.agility = agility
        self.stamina = stamina

    def has_passive(self) -> bool:
        return self.action and self.action.type == Action.PASSIVE
    
    def has_active(self) -> bool:
        return self.action and self.action.type == Action.ACTIVE
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.amount})"

