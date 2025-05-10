import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.cli import run_cli_conversation
from src.core.conversation_handler import ConversationHandler
from src.core.calculator import ProviderCalculator

@pytest.fixture
def mock_input():
    with patch('builtins.input') as mock:
        yield mock

@pytest.fixture
def mock_print():
    with patch('builtins.print') as mock:
        yield mock

class TestCLI:
    def test_initial_greeting(self, mock_input, mock_print):
        mock_input.side_effect = ['yes', '1', '10']  # Simulate user inputs
        run_cli_conversation()
        # Check if welcome message was printed
        mock_print.assert_any_call("Welcome to the Electricity Provider Recommendation Bot!")

    def test_smart_meter_question(self, mock_input, mock_print):
        mock_input.side_effect = ['yes', '1', '10']
        run_cli_conversation()
        # Check if smart meter question was asked
        mock_print.assert_any_call("Do you have (or can install) a smart meter? (yes/no)")

    def test_priority_question(self, mock_input, mock_print):
        mock_input.side_effect = ['yes', '1', '10']
        run_cli_conversation()
        # Check if priority question was asked
        mock_print.assert_any_call("What's most important to you?")
        mock_print.assert_any_call("1) Highest % discount")
        mock_print.assert_any_call("2) Discount during specific hours")

    def test_time_specific_flow(self, mock_input, mock_print):
        mock_input.side_effect = ['yes', '2', '18', '22', '10']
        run_cli_conversation()
        # Check if time-specific questions were asked
        mock_print.assert_any_call("What hour would you like your discount to start? (0-23)")
        mock_print.assert_any_call("What hour would you like your discount to end? (0-23)")

    def test_invalid_smart_meter_input(self, mock_input, mock_print):
        mock_input.side_effect = ['maybe', 'yes', '1', '10']
        run_cli_conversation()
        # Check if error message was shown
        mock_print.assert_any_call("I didn't understand that. Please answer 'yes' or 'no' if you have a smart meter.")

    def test_invalid_priority_input(self, mock_input, mock_print):
        mock_input.side_effect = ['yes', '3', '1', '10']
        run_cli_conversation()
        # Check if error message was shown
        mock_print.assert_any_call("Please enter either 1 (for highest discount) or 2 (for time-specific discount).")

    def test_invalid_hour_input(self, mock_input, mock_print):
        mock_input.side_effect = ['yes', '2', '25', '18', '22', '10']
        run_cli_conversation()
        # Check if error message was shown
        mock_print.assert_any_call("Please enter a valid hour between 0 and 23.")

    def test_recommendation_output(self, mock_input, mock_print):
        mock_input.side_effect = ['yes', '1', '10']
        run_cli_conversation()
        # Check if recommendation was shown
        mock_print.assert_any_call("Recommended Provider:")
        mock_print.assert_any_call("Plan Details:")
        mock_print.assert_any_call("Next Steps:")

    def test_no_suitable_provider(self, mock_input, mock_print):
        mock_input.side_effect = ['no', '1', '50']  # High minimum discount
        run_cli_conversation()
        # Check if no provider message was shown
        mock_print.assert_any_call("Sorry, we couldn't find any suitable providers based on your requirements.") 