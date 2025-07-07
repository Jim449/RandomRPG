import mechanics.action as action
import mechanics.spellEffect as spellEffect
import mechanics.item as item

class Storage:
    def __init__(self):
        self.actions = {}
        self.spell_effects = {}
        self.items = {}
        self.enemies = {}
        self._init_actions()
        
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
        
    def get_action(self, name: str) -> action.Action:
        return self.actions[name]
    
    def get_spell_effect(self, name: str) -> spellEffect.SpellEffect:
        return self.spell_effects[name]
    
    def get_item(self, name: str) -> item.Item:
        return self.items[name]
    