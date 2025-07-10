from conversation import Conversation


class Quest():
    def __init__(self, name: str, step: int = 0):
        """Initializes a quest."""
        self.name = name
        self.step = step
    
    def progress(self) -> None:
        """Increments the quest step."""
        self.step += 1


class QuestLog():
    """Manages the player's quests."""
    def __init__(self):
        self.quests: dict[str, Quest] = {}
    
    def add_quest(self, quest: Quest) -> None:
        """Adds a quest to the quest log."""
        self.quests[quest.name] = quest
    
    def get_quest(self, name: str, step: int = None) -> Quest:
        """Returns a quest from the quest log.
        If step is provided, the quest must be at that step to be returned.
        Return None if no valid quest was found."""
        try:
            quest = self.quests[name]
            if step is None or quest.step == step:
                return quest
            else:
                return None
        except KeyError:
            return None
    
    def get_conversation(self, conversations: list[Conversation]) -> Conversation:
        """Returns a conversation from a list.
        Conversations are selected with the following priority:

        1. Conversations which are linked to quests and don't require a player choice.
        
        2. Conversations which are linked to quests and do require a player choice.
        
        3. Conversations which are unrelated to quests.
        
        The player must meet the quest step requirement to trigger the conversation.
        As of now, some conversation may permanently fail to trigger
        if other conversations of equal or higher priority are present."""
        result = None

        for conversation in conversations:
            if conversation.quest_name is None:
                if result is None:
                    result = conversation
            else:
                quest = self.get_quest(conversation.quest_name, conversation.quest_step)
                
                if not quest:
                    continue
                if not conversation.confirmation:
                    return conversation
                else:
                    result = conversation
        return result

    def finish_conversation(self, conversation: Conversation) -> None:
        """Finishes a conversation and updates the quest log accordingly."""
        if conversation.quest_name is not None:
            quest = self.get_quest(conversation.quest_name, conversation.quest_step)
            if quest:
                quest.progress()

        if conversation.quest_initiation is not None:
            self.add_quest(Quest(conversation.quest_initiation))

    