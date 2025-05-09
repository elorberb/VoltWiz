"""
Conversation handler module for managing user interactions.
"""

from enum import Enum
from typing import Dict, Optional, Tuple

class ConversationState(Enum):
    """
    Enum representing the different states of a conversation.
    """
    INITIAL = 0
    ASKING_SMART_METER = 1
    ASKING_PRIORITY = 2
    ASKING_DISCOUNT_START = 3
    ASKING_DISCOUNT_END = 4
    ASKING_MIN_DISCOUNT = 5
    COMPLETED = 6

class UserState:
    """
    Class representing the state of a user in a conversation.
    """
    def __init__(self):
        self.state = ConversationState.INITIAL
        self.has_smart_meter = None
        self.priority = None  # "max_discount" or "time_specific"
        self.discount_window = None  # Tuple of (start_hour, end_hour)
        self.min_discount_pct = 0.0  # Default to 0% minimum discount

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

    def get_next_question(self, user_id: str) -> str:
        """
        Get the next question to ask the user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The next question to ask, or None if the conversation is complete
        """
        state = self.get_user_state(user_id)

        if state.state == ConversationState.INITIAL:
            state.state = ConversationState.ASKING_SMART_METER
            return "Do you have (or can install) a smart meter? (yes/no)"

        elif state.state == ConversationState.ASKING_SMART_METER:
            state.state = ConversationState.ASKING_PRIORITY
            return ("What's most important to you?\n"
                    "1) Highest % discount\n"
                    "2) Discount during specific hours\n"
                    "Enter 1 or 2:")

        elif state.state == ConversationState.ASKING_PRIORITY:
            if state.priority == "time_specific":
                state.state = ConversationState.ASKING_DISCOUNT_START
                return "What hour would you like your discount to start? (0-23)"
            else:
                state.state = ConversationState.ASKING_MIN_DISCOUNT
                return "What is your minimum acceptable discount percentage? (e.g., 10)"

        elif state.state == ConversationState.ASKING_DISCOUNT_START:
            state.state = ConversationState.ASKING_DISCOUNT_END
            return "What hour would you like your discount to end? (0-23)"

        elif state.state == ConversationState.ASKING_DISCOUNT_END:
            state.state = ConversationState.ASKING_MIN_DISCOUNT
            return "What is your minimum acceptable discount percentage? (e.g., 10)"

        elif state.state == ConversationState.ASKING_MIN_DISCOUNT:
            state.state = ConversationState.COMPLETED
            return None

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
            answer_lower = answer.lower()
            if answer_lower in ['yes', 'y', 'true', 'yeah', '1']:
                state.has_smart_meter = True
                return self.get_next_question(user_id)
            elif answer_lower in ['no', 'n', 'false', 'nope', '0']:
                state.has_smart_meter = False
                return self.get_next_question(user_id)
            else:
                return "I didn't understand that. Please answer 'yes' or 'no' if you have a smart meter."

        elif state.state == ConversationState.ASKING_PRIORITY:
            answer = answer.strip()
            if answer == "1":
                state.priority = "max_discount"
                return self.get_next_question(user_id)
            elif answer == "2":
                state.priority = "time_specific"
                return self.get_next_question(user_id)
            else:
                return "Please enter either 1 (for highest discount) or 2 (for time-specific discount)."

        elif state.state == ConversationState.ASKING_DISCOUNT_START:
            try:
                start_hour = int(answer.strip())
                if 0 <= start_hour <= 23:
                    # Store temporarily until we get the end hour
                    state.discount_window = (start_hour, None)
                    return self.get_next_question(user_id)
                else:
                    return "Please enter a valid hour between 0 and 23."
            except ValueError:
                return "Please enter a valid hour between 0 and 23."

        elif state.state == ConversationState.ASKING_DISCOUNT_END:
            try:
                end_hour = int(answer.strip())
                if 0 <= end_hour <= 23:
                    # Complete the discount window tuple
                    start_hour = state.discount_window[0]
                    state.discount_window = (start_hour, end_hour)
                    return self.get_next_question(user_id)
                else:
                    return "Please enter a valid hour between 0 and 23."
            except ValueError:
                return "Please enter a valid hour between 0 and 23."

        elif state.state == ConversationState.ASKING_MIN_DISCOUNT:
            try:
                min_discount = float(answer.strip())
                if min_discount < 0:
                    return "Minimum discount percentage cannot be negative. Please enter a valid percentage."
                if min_discount > 100:
                    return "Discount percentage cannot exceed 100%. Please enter a valid percentage."
                state.min_discount_pct = min_discount
                return self.get_next_question(user_id)
            except ValueError:
                # If the user doesn't enter anything or enters an invalid value, default to 0
                if not answer.strip():
                    state.min_discount_pct = 0.0
                    return self.get_next_question(user_id)
                return "Please enter a valid discount percentage (e.g., 10) or leave empty for no minimum."

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
