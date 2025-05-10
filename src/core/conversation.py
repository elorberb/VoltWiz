from enum import Enum
from typing import Dict, Optional

class ConversationState(Enum):
    """
    Enum representing the different states of a conversation.
    """
    INITIAL = 0
    ASKING_VENDOR = 1
    ASKING_SMART_METER = 2
    ASKING_DISCOUNT_TYPE = 3
    ASKING_DISCOUNT_START = 4
    ASKING_DISCOUNT_END = 5
    ASKING_MIN_DISCOUNT = 6
    COMPLETED = 7

class UserState:
    """
    Class representing the state of a user in a conversation.
    """
    def __init__(self):
        self.state = ConversationState.INITIAL
        self.vendor = None  # "hot", "amisragaz", or "none"
        self.has_smart_meter = None
        self.discount_type = None  # "all_day" or "specific_hours"
        self.discount_window = None  # List of [start_hour, end_hour]
        self.min_discount_pct = 0.0

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
            state.state = ConversationState.ASKING_VENDOR
            return ("האם אתם לקוחות של אחת מהחברות הבאות?\n"
                   "1) HOT\n"
                   "2) אמישראגז\n"
                   "3) אף אחת מהן")

        elif state.state == ConversationState.ASKING_VENDOR:
            state.state = ConversationState.ASKING_SMART_METER
            return "האם יש לכם (או תוכלו להתקין) מונה חכם? (כן/לא)"

        elif state.state == ConversationState.ASKING_SMART_METER:
            state.state = ConversationState.ASKING_DISCOUNT_TYPE
            return "האם אתם מעדיפים הנחה:\n1) לאורך כל היום\n2) בשעות ספציפיות"

        elif state.state == ConversationState.ASKING_DISCOUNT_TYPE:
            if state.discount_type == "specific_hours":
                state.state = ConversationState.ASKING_DISCOUNT_START
                return "באיזו שעה תרצו שההנחה תתחיל? (0-23)"
            else:
                state.state = ConversationState.ASKING_MIN_DISCOUNT
                return "מה אחוז ההנחה המינימלי שאתם מחפשים? (הזינו מספר)"

        elif state.state == ConversationState.ASKING_DISCOUNT_START:
            state.state = ConversationState.ASKING_DISCOUNT_END
            return "באיזו שעה תרצו שההנחה תסתיים? (0-23)"

        elif state.state == ConversationState.ASKING_DISCOUNT_END:
            state.state = ConversationState.ASKING_MIN_DISCOUNT
            return "מה אחוז ההנחה המינימלי שאתם מחפשים? (הזינו מספר)"

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

        if state.state == ConversationState.ASKING_VENDOR:
            try:
                choice = int(answer)
                if choice == 1:
                    state.vendor = "hot"
                elif choice == 2:
                    state.vendor = "amisragaz"
                elif choice == 3:
                    state.vendor = "none"
                else:
                    return "אנא הזינו מספר בין 1 ל-3."
                return self.get_next_question(user_id)
            except ValueError:
                return "אנא הזינו מספר בין 1 ל-3."

        elif state.state == ConversationState.ASKING_SMART_METER:
            answer = answer.lower()
            if answer in ['כן', 'yes', 'y', 'true']:
                state.has_smart_meter = True
            elif answer in ['לא', 'no', 'n', 'false']:
                state.has_smart_meter = False
            else:
                return "לא הבנתי. אנא ענו 'כן' או 'לא' אם יש לכם מונה חכם."
            return self.get_next_question(user_id)

        elif state.state == ConversationState.ASKING_DISCOUNT_TYPE:
            try:
                choice = int(answer)
                if choice == 1:
                    state.discount_type = "all_day"
                elif choice == 2:
                    state.discount_type = "specific_hours"
                else:
                    return "אנא הזינו 1 (להנחה לאורך כל היום) או 2 (להנחה בשעות ספציפיות)."
                return self.get_next_question(user_id)
            except ValueError:
                return "אנא הזינו 1 (להנחה לאורך כל היום) או 2 (להנחה בשעות ספציפיות)."

        elif state.state == ConversationState.ASKING_DISCOUNT_START:
            try:
                hour = int(answer)
                if 0 <= hour <= 23:
                    state.discount_window = [hour]
                    return self.get_next_question(user_id)
                else:
                    return "אנא הזינו שעה תקינה בין 0 ל-23."
            except ValueError:
                return "אנא הזינו שעה תקינה בין 0 ל-23."

        elif state.state == ConversationState.ASKING_DISCOUNT_END:
            try:
                hour = int(answer)
                if 0 <= hour <= 23:
                    state.discount_window.append(hour)
                    return self.get_next_question(user_id)
                else:
                    return "אנא הזינו שעה תקינה בין 0 ל-23."
            except ValueError:
                return "אנא הזינו שעה תקינה בין 0 ל-23."

        elif state.state == ConversationState.ASKING_MIN_DISCOUNT:
            try:
                discount = float(answer)
                if discount >= 0:
                    state.min_discount_pct = discount
                    return self.get_next_question(user_id)
                else:
                    return "אנא הזינו אחוז הנחה חיובי."
            except ValueError:
                return "אנא הזינו מספר תקין לאחוז ההנחה."

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
