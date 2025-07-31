from typing import Self

class Conversation():
    """A class used to display messages to the player.
    Used to start and progress quests."""
    def __init__(self, message: list[str],
                 quest_name: str = None,
                 quest_step: int = None,
                 quest_initiation: str = None,
                 progress_quest: bool = True,
                 item: str = None,
                 spell: str = None,
                 heal: bool = False,
                 restore: bool = False,
                 reward: int = 0,
                 prompt: str = None,
                 cost: int = 0):
        self.message = message
        self.accept_conversation: Self = None
        self.reject_conversation: Self = None
        self.quest_name: str = quest_name
        self.quest_step: int = quest_step
        self.quest_initiation: str = quest_initiation
        self.progress_quest: bool = progress_quest
        self.current_message = 0
        self.confirmation: bool = False
        self.confirmation_y: int = 0
        self.prompt: str = prompt
        self.cost: int = cost
        self.reward: int = reward
        self.item: str = item
        self.spell: str = spell
        self.heal: bool = heal
        self.restore: bool = restore

    def add_accept_conversation(self, conversation: Self) -> None:
        """Adds a conversation that will be triggered
        if the player selects yes at the prompt.
        The player may have to pay a cost to trigger the conversation."""
        self.accept_conversation = conversation
        self.confirmation = True
    
    def add_reject_conversation(self, conversation: Self) -> None:
        """Adds a conversation that will be triggered
        if the player selects no at the prompt."""
        self.reject_conversation = conversation
        self.confirmation = True
    
    def add_quest(self, quest_name: str, quest_step: int,
                  progress_quest: bool = True,
                  quest_initiation: str = None) -> None:
        """Links the conversation to a quest.
        The conversation is only triggered if the player is at the given quest step.
        If progress_quest is True, the quest step will be incremented.
        If there is a quest_initiation, a new quest is started at step 1.
        """
        self.quest_name = quest_name
        self.quest_step = quest_step
        self.progress_quest = progress_quest
        self.quest_initiation = quest_initiation
    
    def add_reward(self, item: str = None, spell: str = None,
                   heal: bool = False, restore: bool = False,
                   reward: int = 0) -> None:
        """Adds a reward to the conversation.
        The reward can be an item, healing, magic restoration or coins."""
        self.item = item
        self.spell = spell
        self.heal = heal
        self.restore = restore
        self.reward = reward
    
    def get_message(self) -> str:
        """Returns the current message and proceeds to the next one."""
        if self.current_message < len(self.message):
            message = self.message[self.current_message]
            self.current_message += 1
            return message
        else:
            return None
    
    def awaiting_confirmation(self) -> bool:
        """Returns True if the conversation is awaiting confirmation."""
        if self.confirmation and self.current_message == len(self.message):
            return True
        else:
            return False
    
    def increase_confirmation_y(self) -> None:
        if self.confirmation_y == 0:
            self.confirmation_y = 1
        else:
            self.confirmation_y = 0
    
    def get_confirmation_y(self) -> int:
        """Returns the current confirmation y."""
        return self.confirmation_y
    
    def reset(self) -> None:
        """Resets the conversation to the first message."""
        self.current_message = 0
        self.confirmation_y = 0

    def __str__(self) -> str:
        return f"Quest {self.quest_name} at step {self.quest_step}: {self.message[0]}..."