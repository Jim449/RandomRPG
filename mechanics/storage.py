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
        # Should be obtainable in the Meadows, perhaps as an early quest reward
        # Could be a delivery quest for reaching a specific house
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

        # Should be obtainable early
        # Perhaps as a sold item in the first shop, in the Meadows
        # Shouldn't there be more stuff for sale?
        new_item = item.Item("Gray hide",
                             "A silvery gray hide made from wolf fur. It's quite durable.",
                             type=item.Item.ARMOR,
                             defense=1)
        self.items[new_item.name] = new_item

        # A basic weapon, but it should feel special getting more strength
        # A possible quest reward for defeating a minor boss
        # Or a quest reward given beyond the first area
        new_item = item.Item("Sabre",
                             "An elegant weapon with a curved blade.",
                             type=item.Item.WEAPON,
                             strength=1)
        self.items[new_item.name] = new_item

        # An early armor, obtainable from a quest
        # An alternative to the gray hide,
        # the Oakgrove weave is better when you can defeat your opponents quickly
        new_item = item.Item("Oakgrove weave",
                             "A cloth worn by rangers. It carries the vitality of nature.",
                             type=item.Item.ARMOR,
                             stamina=1)
        self.items[new_item.name] = new_item

        # The first item which raises magic
        # It should be obtainable before the first boss
        # and gives the player access to new strategies
        # At that point, the player should already have the Sabre
        new_item = item.Item("Ash staff",
                             "A pale staff carrying a gentle power.",
                             type=item.Item.WEAPON,
                             intelligence=1)
        self.items[new_item.name] = new_item
        
        # Items which raise resistance are quite niche
        # It could be a decent reward for slaying the first boss
        new_item = item.Item("Mystical idol",
                             "A charm which wards off evil.",
                             type=item.Item.MISC,
                             resistance=1)
        self.items[new_item.name] = new_item

        new_item = item.Item("Divine blade",
                             "A blade which glows with divine energy.",
                             type=item.Item.WEAPON,
                             strength=100)
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
                              team=0, level=level)
            enemy.set_actions(actions)
            enemy.set_stats(CharacterStats(data["stats"]))
            return enemy

    def get_enemies(self, names: list[str], levels: list[int]) -> list[unit.Unit]:
        """Returns a list of enemies with the given names and levels."""
        enemies = []

        for name, level in zip(names, levels):
            enemies.append(self.get_enemy(name, level))

        return enemies
