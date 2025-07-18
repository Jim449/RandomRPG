from typing import Self

class Conversation():
    """A class used to display messages to the player.
    Used to start and progress quests."""
    def __init__(self, messages: list[str]):
        self.messages = messages
        self.accept_conversation: Self = None
        self.reject_conversation: Self = None
        self.quest_name: str = None
        self.quest_step: int = None
        self.quest_initiation: str = None
        self.progress_quest: bool = True
        self.current_message = 0
        self.confirmation: bool = False
        self.confirmation_y: int = 0
        self.prompt: str = None
        self.cost: int = 0
        self.reward: int = 0
        self.item: str = None
        self.heal: bool = False
        self.restore: bool = False

    def add_accept_conversation(self, conversation: Self, prompt: str, cost: int = 0) -> None:
        """Adds a conversation that will be triggered
        if the player selects yes at the prompt.
        The player may have to pay a cost to trigger the conversation."""
        self.accept_conversation = conversation
        self.confirmation = True
        self.prompt = prompt
        self.cost = cost
    
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
    
    def add_reward(self, item: str = None, heal: bool = False, restore: bool = False,
                   reward: int = 0) -> None:
        """Adds a reward to the conversation.
        The reward can be an item, healing, magic restoration or coins."""
        self.item = item
        self.heal = heal
        self.restore = restore
        self.reward = reward
    
    def get_message(self) -> str:
        """Returns the current message and proceeds to the next one."""
        if self.current_message < len(self.messages):
            message = self.messages[self.current_message]
            self.current_message += 1
            return message
        else:
            return None
    
    def awaiting_confirmation(self) -> bool:
        """Returns True if the conversation is awaiting confirmation."""
        if self.confirmation and self.current_message == len(self.messages):
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