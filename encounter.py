from conversation import Conversation
from typing import Self
from quest_log import QuestLog

class Encounter:
    """Represents an enemy encounter.
    The units are not instantiated and should be fetched from the storage."""
    def __init__(self, enemies: list[str], levels: list[int],
                 encounter_weight: int = 1,
                 conversation: Conversation = None,
                 conversation_name: str = None,
                 conversation_index: int = 0,
                 reward: int = 0,
                 allow_escape: bool = False,
                 block_escape: bool = False):
        """Creates a new encounter with the given enemies.
        The enemies must be fetched from the storage.
        The encounter_weight determines the chance of the encounter being triggered.
        A coin reward can be set.
        The conversation can be used to set encounter requirements.
        It can also be used to advance quests or give rewards.
        Use this to hand out one-time rewards."""
        self.names = enemies
        self.levels = levels
        self.units = []
        self.encounter_weight = encounter_weight
        self.conversation = conversation
        # The conversation should be loaded from the storage upon encounter start
        # This should make it easier to save and load encounters    
        self.conversation_name = conversation_name
        self.conversation_index = conversation_index
        self.reward = reward
        self.allow_escape = allow_escape
        self.block_escape = block_escape
    
    def instantiate(self, storage) -> Self:
        """Fetches the units from the storage.
        Returns a new encounter with the units."""
        encounter = Encounter(self.names, self.levels, self.encounter_weight,
                              self.conversation, self.reward)
        encounter.units = storage.get_enemies(self.names, self.levels)
        if self.conversation_name:
            encounter.conversation = storage.get_conversation(self.conversation_name, self.conversation_index)
        return encounter
    
    def check_requirements(self, quest_log: QuestLog) -> bool:
        """Checks if the encounter can be triggered."""
        if self.conversation is None:
            return True
        else:
            return quest_log.check_conversation(self.conversation)

    def get_experience(self) -> int:
        """Returns the experience points for the encounter."""
        return sum([unit.get_experience() for unit in self.units])
    
    def get_coins(self) -> int:
        """Returns the coin reward for the encounter."""
        return self.reward

    def finish_encounter(self, quest_log: QuestLog) -> None:
        """Updates the quest log with the encounter's conversation."""
        if self.conversation is not None:
            quest_log.finish_conversation(self.conversation)
    
    def get_save_game_dict(self) -> dict:
        data = {
            "names": self.names,
            "levels": self.levels,
            "conversation_name": self.conversation_name,
            "conversation_index": self.conversation_index,
            "encounter_weight": self.encounter_weight,
            "reward": self.reward,
            "allow_escape": self.allow_escape,
            "block_escape": self.block_escape
        }
        return data
