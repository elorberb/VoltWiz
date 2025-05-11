from enum import Enum
from typing import Dict, Optional

class ConversationState(Enum):
    """
    Enum representing the different states of a conversation.
    """
    INITIAL = 0
    ASKING_SMART_METER = 1
    ASKING_DISCOUNT_TYPE = 2
    ASKING_TIME_PREFERENCE = 3
    ASKING_VENDOR = 4
    COMPLETED = 5

class UserState:
    """
    Class representing the state of a user in a conversation.
    """
    def __init__(self):
        self.state = ConversationState.INITIAL
        self.has_smart_meter = None
        self.discount_type = None  # "fixed" or "variable"
        self.time_preference = None  # "day" or "night"
        self.vendor = None  # "hot", "amisragaz", or "none"

class ConversationHandler:
    """
    Handler for managing conversations with users.
    """
    def __init__(self):
        self.user_states: Dict[str, UserState] = {}

    def get_user_state(self, user_id: str) -> UserState:
        """
        Get the state of a user in a conversation.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The user's state
        """
        if user_id not in self.user_states:
            self.user_states[user_id] = UserState()
        return self.user_states[user_id]

    def get_next_question(self, user_id: str) -> tuple[str, list[list[str]]]:
        """
        Returns the next question and available buttons.
        Returns a tuple of (question_text, button_options)
        """
        state = self.get_user_state(user_id)
        
        if state.state == ConversationState.INITIAL:
            state.state = ConversationState.ASKING_SMART_METER
            return "האם יש לכם שעון חכם?", [["כן", "לא"]]
        
        elif state.state == ConversationState.ASKING_SMART_METER:
            if state.has_smart_meter:
                state.state = ConversationState.ASKING_DISCOUNT_TYPE
                return "איזה סוג הנחה אתם מעדיפים?", [["הנחה קבועה", "הנחה בשעות משתנות"]]
            else:
                state.state = ConversationState.ASKING_VENDOR
                return "האם אתם לקוחות של אחת מהחברות הבאות?", [["הוט", "אמישראגז", "אף אחד מהם"]]
        
        elif state.state == ConversationState.ASKING_DISCOUNT_TYPE:
            if state.discount_type == "variable":
                state.state = ConversationState.ASKING_TIME_PREFERENCE
                return "באיזו שעות אתם מעדיפים את ההנחה?", [["יום (7:00-17:00)", "לילה (23:00-7:00)"]]
            else:
                state.state = ConversationState.ASKING_VENDOR
                return "האם אתם לקוחות של אחת מהחברות הבאות?", [["הוט", "אמישראגז", "אף אחד מהם"]]
        
        elif state.state == ConversationState.ASKING_TIME_PREFERENCE:
            state.state = ConversationState.ASKING_VENDOR
            return "האם אתם לקוחות של אחת מהחברות הבאות?", [["הוט", "אמישראגז", "אף אחד מהם"]]
        
        elif state.state == ConversationState.ASKING_VENDOR:
            state.state = ConversationState.COMPLETED
            return None, None

    def process_answer(self, user_id: str, answer: str) -> Optional[str]:
        """
        Process the user's answer and return the next question.
        
        Args:
            user_id: The ID of the user
            answer: The user's answer
            
        Returns:
            The next question to ask, or None if the conversation is complete
        """
        state = self.get_user_state(user_id)
        
        if state.state == ConversationState.ASKING_SMART_METER:
            answer = answer.lower()
            if answer in ['כן', 'yes', 'y', 'true']:
                state.has_smart_meter = True
            elif answer in ['לא', 'no', 'n', 'false']:
                state.has_smart_meter = False
            else:
                return "לא הבנתי. אנא בחר 'כן' או 'לא'."
            return None
        
        elif state.state == ConversationState.ASKING_DISCOUNT_TYPE:
            if answer == "הנחה קבועה":
                state.discount_type = "fixed"
            elif answer == "הנחה בשעות משתנות":
                state.discount_type = "variable"
            else:
                return "אנא בחר אחת מהאפשרויות המוצגות."
            return None
        
        elif state.state == ConversationState.ASKING_TIME_PREFERENCE:
            if answer == "יום (7:00-17:00)":
                state.time_preference = "day"
            elif answer == "לילה (23:00-7:00)":
                state.time_preference = "night"
            else:
                return "אנא בחר אחת מהאפשרויות המוצגות."
            return None
        
        elif state.state == ConversationState.ASKING_VENDOR:
            if answer == "הוט":
                state.vendor = "hot"
            elif answer == "אמישראגז":
                state.vendor = "amisragaz"
            elif answer == "אף אחד מהם":
                state.vendor = "none"
            else:
                return "אנא בחר אחת מהאפשרויות המוצגות."
            return None
        
        return None

    def is_conversation_complete(self, user_id: str) -> bool:
        """
        Check if the conversation with the user is complete.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            True if the conversation is complete, False otherwise
        """
        state = self.get_user_state(user_id)
        return state.state == ConversationState.COMPLETED

    def get_user_data(self, user_id: str) -> Optional[UserState]:
        """
        Get the user's data if the conversation is complete.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The user's state if the conversation is complete, None otherwise
        """
        state = self.get_user_state(user_id)
        if self.is_conversation_complete(user_id):
            return state
        return None

    def reset_conversation(self, user_id: str):
        """
        Reset the conversation with the user.
        
        Args:
            user_id: The ID of the user
        """
        self.user_states[user_id] = UserState()
