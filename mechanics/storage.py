import mechanics.action as action
import mechanics.spellEffect as spellEffect
import mechanics.item as item
import unit
from pygame import image
from mechanics.characterStats import CharacterStats
import json

class Storage:
    def __init__(self):
        self.actions = {}
        self.spell_effects = {}
        self.items = {}
        self._init_actions()
        self._init_items()
        
    def _init_actions(self):
        new_action = action.Action("Attack", target_ally=False,
                                   action_function=action.attack,
                                   print_action_name=False)
        self.actions[new_action.name] = new_action
        new_action = action.Action("Defend", target_ally=False,
                                   action_function=action.defend,
                                   print_action_name=False)
        self.actions[new_action.name] = new_action
        new_action = action.Action("Inaction", target_ally=False,
                                   action_function=action.inaction,
                                   print_action_name=False)
        self.actions[new_action.name] = new_action
    
    def _init_items(self):
        new_item = item.Item("Spiders shawl",
                             "A light shawl with a faint red tone. It makes the wearer feel nimble.",
                             type=item.Item.MISC,
                             agility=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Silkcutter",
                             "A sharp dagger which Richard used to battle the spiders. It makes its wielder feel nimble.",
                             type=item.Item.WEAPON,
                             agility=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Spiders tunic",
                             "A fine tunic made from silk. It gives its wielder the agility of a spider.",
                             type=item.Item.ARMOR,
                             agility=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Quarterstaff",
                             "A wooden staff. While weak, it's excellent for warding off attackers.",
                             type=item.Item.WEAPON,
                             defense=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Chainmail",
                             "A sturdy chainmail.",
                             type=item.Item.ARMOR,
                             defense=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Obsidian ring",
                             "A ring with a faceted obsidian stone. It protects its user from harm.",
                             type=item.Item.MISC,
                             defense=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Sabre",
                             "An elegant weapon with a curved blade.",
                             type=item.Item.WEAPON,
                             strength=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Gray hide",
                             "A silvery gray hide made from wolf fur. It has a feral power to it.",
                             type=item.Item.ARMOR,
                             strength=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Wolfs claw",
                             "A necklace made from a wolfs claw. It looks deadly.",
                             type=item.Item.MISC,
                             strength=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Crescent cutter",
                             "A moon-shaped knife, used by druids to harvest healing herbs.",
                             type=item.Item.WEAPON,
                             stamina=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Oakgrove weave",
                             "A cloth worn by rangers. It carries the vitality of nature.",
                             type=item.Item.ARMOR,
                             stamina=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Oak amulet",
                             "A charm which brings good health.",
                             type=item.Item.MISC,
                             stamina=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Ash staff",
                             "A pale staff carrying a gentle power.",
                             type=item.Item.WEAPON,
                             intelligence=1)
        self.items[new_item.name] = new_item
        
        new_item = item.Item("Mage cloak",
                             "An exclusive cloak which eases the burden of casting spells.",
                             type=item.Item.ARMOR,
                             intelligence=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Mana crystal",
                             "Used by mages to store magical powers.",
                             type=item.Item.MISC,
                             intelligence=1)
        self.items[new_item.name] = new_item

    def get_action(self, name: str) -> action.Action:
        return self.actions[name]
    
    def get_spell_effect(self, name: str) -> spellEffect.SpellEffect:
        return self.spell_effects[name]
    
    def get_item(self, name: str) -> item.Item:
        return self.items[name]
    
    def get_enemy(self, name: str, level: int = 1) -> unit.Unit:
        """Returns a single enemy with the given name."""
        with open(f"resources/stats/{name}.json", "r") as file:
            data = json.load(file)
            actions = []

            for move in data["moveset"]:
                actions.append(self.get_action(move))
                
            enemy = unit.Unit(data["name"], image.load(f"resources/enemies/{name}.png"),
                              team=0, level=level,
                              blink_sprite=image.load(f"resources/enemies/{name}_RED.png"))
            enemy.set_actions(actions)
            enemy.set_stats(CharacterStats(data["stats"]))
            return enemy

    def get_enemies(self, names: list[str], levels: list[int]) -> list[unit.Unit]:
        """Returns a list of enemies with the given names and levels."""
        enemies = []

        for name, level in zip(names, levels):
            enemies.append(self.get_enemy(name, level))

        return enemies
