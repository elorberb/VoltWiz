import pytest
from src.core.conversation_handler import ConversationHandler, ConversationState

@pytest.fixture
def handler():
    """Create a conversation handler instance for testing."""
    return ConversationHandler()

@pytest.fixture
def user_id():
    """Return a test user ID."""
    return "test_user"

class TestConversationHandler:
    def test_initial_state(self, handler, user_id):
        state = handler.get_user_state(user_id)
        assert state.state == ConversationState.INITIAL
        assert state.has_smart_meter is None
        assert state.priority is None
        assert state.discount_window is None
        assert state.min_discount_pct == 0.0

    def test_smart_meter_question(self, handler, user_id):
        question = handler.get_next_question(user_id)
        assert "smart meter" in question.lower()
        assert handler.get_user_state(user_id).state == ConversationState.ASKING_SMART_METER

    def test_priority_question_after_smart_meter(self, handler, user_id):
        handler.get_next_question(user_id)  # Get smart meter question
        next_q = handler.process_answer(user_id, "yes")
        assert "important" in next_q.lower()
        assert handler.get_user_state(user_id).state == ConversationState.ASKING_PRIORITY

    def test_time_specific_flow(self, handler, user_id):
        # Answer smart meter question
        handler.get_next_question(user_id)
        handler.process_answer(user_id, "yes")
        # Answer priority question
        handler.process_answer(user_id, "2")  # Time specific
        # Should ask for start hour
        state = handler.get_user_state(user_id)
        assert state.state == ConversationState.ASKING_DISCOUNT_START
        assert state.priority == "time_specific"

    def test_max_discount_flow(self, handler, user_id):
        # Answer smart meter question
        handler.get_next_question(user_id)
        handler.process_answer(user_id, "yes")
        # Answer priority question
        handler.process_answer(user_id, "1")  # Max discount
        # Should ask for minimum discount
        state = handler.get_user_state(user_id)
        assert state.state == ConversationState.ASKING_MIN_DISCOUNT
        assert state.priority == "max_discount"

    @pytest.mark.parametrize("invalid_input,expected_message", [
        ("maybe", "didn't understand"),
        ("", "didn't understand"),
        ("y", "didn't understand")
    ])
    def test_invalid_smart_meter_answers(self, handler, user_id, invalid_input, expected_message):
        handler.get_next_question(user_id)
        response = handler.process_answer(user_id, invalid_input)
        assert expected_message in response.lower()
        assert handler.get_user_state(user_id).state == ConversationState.ASKING_SMART_METER

    @pytest.mark.parametrize("invalid_input,expected_message", [
        ("3", "enter either 1"),
        ("0", "enter either 1"),
        ("abc", "enter either 1")
    ])
    def test_invalid_priority_answers(self, handler, user_id, invalid_input, expected_message):
        handler.get_next_question(user_id)
        handler.process_answer(user_id, "yes")
        response = handler.process_answer(user_id, invalid_input)
        assert expected_message in response.lower()
        assert handler.get_user_state(user_id).state == ConversationState.ASKING_PRIORITY

    @pytest.mark.parametrize("invalid_hour,expected_message", [
        ("25", "valid hour"),
        ("-1", "valid hour"),
        ("abc", "valid hour")
    ])
    def test_invalid_hour_inputs(self, handler, user_id, invalid_hour, expected_message):
        # Get to hour input
        handler.get_next_question(user_id)
        handler.process_answer(user_id, "yes")
        handler.process_answer(user_id, "2")
        # Try invalid hour
        response = handler.process_answer(user_id, invalid_hour)
        assert expected_message in response.lower()
        assert handler.get_user_state(user_id).state == ConversationState.ASKING_DISCOUNT_START

    def test_conversation_completion(self, handler, user_id):
        # Complete the conversation
        handler.get_next_question(user_id)
        handler.process_answer(user_id, "yes")
        handler.process_answer(user_id, "1")
        handler.process_answer(user_id, "10")
        
        assert handler.is_conversation_complete(user_id)
        user_data = handler.get_user_data(user_id)
        assert user_data is not None
        assert user_data.has_smart_meter is True
        assert user_data.priority == "max_discount"
        assert user_data.min_discount_pct == 10.0

    def test_reset_conversation(self, handler, user_id):
        # Complete the conversation
        handler.get_next_question(user_id)
        handler.process_answer(user_id, "yes")
        handler.process_answer(user_id, "1")
        handler.process_answer(user_id, "10")
        
        # Reset and verify
        handler.reset_conversation(user_id)
        state = handler.get_user_state(user_id)
        assert state.state == ConversationState.INITIAL
        assert state.has_smart_meter is None
        assert state.priority is None
        assert state.discount_window is None
        assert state.min_discount_pct == 0.0 