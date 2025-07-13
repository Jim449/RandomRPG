from conversation import Conversation
from mechanics.storage import Storage
from typing import Self
from quest_log import QuestLog

class Encounter:
    """Represents an enemy encounter.
    The units are not instantiated and should be fetched from the storage."""
    def __init__(self, enemies: list[str], level: list[int],
                 encounter_weight: int = 1,
                 conversation: Conversation = None,
                 reward: int = 0):
        """Creates a new encounter with the given enemies.
        The enemies must be fetched from the storage.
        The encounter_weight determines the chance of the encounter being triggered.
        A coin reward can be set.
        The conversation can be used to set encounter requirements.
        It can also be used to advance quests or give rewards.
        Use this to hand out one-time rewards."""
        self.names = enemies
        self.level = level
        self.units = []
        self.encounter_weight = encounter_weight
        self.conversation = conversation
        self.reward = reward
    
    def instantiate(self, storage: Storage) -> Self:
        """Fetches the units from the storage.
        Returns a new encounter with the units."""
        encounter = Encounter(self.names, self.level, self.encounter_weight,
                              self.conversation, self.reward)
        encounter.units = storage.get_enemies(self.names, self.level)
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

    def finish_encounter(self, quest_log: QuestLog) -> None:
        """Updates the quest log with the encounter's conversation."""
        if self.conversation is not None:
            quest_log.finish_conversation(self.conversation)