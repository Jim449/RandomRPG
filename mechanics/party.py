from mechanics.character import Character
from mechanics.inventory import Inventory

class Party:
    def __init__(self, characters: list[Character]):
        self.characters = characters
        self.inventory = Inventory()

    def get_characters(self) -> list[Character]:
        return self.characters