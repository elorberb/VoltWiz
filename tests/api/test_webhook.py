import pytest
from flask import Flask
from api.webhook import create_app
from core.conversation_handler import ConversationHandler
from core.calculator import ProviderCalculator

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def test_phone():
    """Return a test phone number."""
    return 'whatsapp:+1234567890'

class TestWebhook:
    def test_initial_message(self, client, test_phone):
        response = client.post('/webhook', data={
            'Body': 'hi',
            'From': test_phone
        })
        assert response.status_code == 200
        assert 'Welcome' in response.data.decode()
        assert 'smart meter' in response.data.decode()

    def test_smart_meter_yes(self, client, test_phone):
        # First message
        client.post('/webhook', data={
            'Body': 'hi',
            'From': test_phone
        })
        # Answer smart meter question
        response = client.post('/webhook', data={
            'Body': 'yes',
            'From': test_phone
        })
        assert response.status_code == 200
        assert 'important' in response.data.decode()

    def test_max_discount_flow(self, client, test_phone):
        # Complete the conversation flow
        client.post('/webhook', data={
            'Body': 'hi',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': 'yes',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': '1',
            'From': test_phone
        })
        response = client.post('/webhook', data={
            'Body': '10',
            'From': test_phone
        })
        assert response.status_code == 200
        assert 'Recommended Provider' in response.data.decode()

    def test_time_specific_flow(self, client, test_phone):
        # Complete the conversation flow
        client.post('/webhook', data={
            'Body': 'hi',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': 'yes',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': '2',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': '18',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': '22',
            'From': test_phone
        })
        response = client.post('/webhook', data={
            'Body': '10',
            'From': test_phone
        })
        assert response.status_code == 200
        assert 'Recommended Provider' in response.data.decode()

    @pytest.mark.parametrize("invalid_input,expected_message", [
        ("maybe", "didn't understand"),
        ("", "didn't understand"),
        ("y", "didn't understand")
    ])
    def test_invalid_smart_meter_inputs(self, client, test_phone, invalid_input, expected_message):
        # First message
        client.post('/webhook', data={
            'Body': 'hi',
            'From': test_phone
        })
        # Invalid smart meter answer
        response = client.post('/webhook', data={
            'Body': invalid_input,
            'From': test_phone
        })
        assert response.status_code == 200
        assert expected_message in response.data.decode()

    def test_restart_conversation(self, client, test_phone):
        # Complete a conversation
        client.post('/webhook', data={
            'Body': 'hi',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': 'yes',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': '1',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': '10',
            'From': test_phone
        })
        
        # Start over
        response = client.post('/webhook', data={
            'Body': 'hi',
            'From': test_phone
        })
        assert response.status_code == 200
        assert 'Welcome' in response.data.decode()
        assert 'smart meter' in response.data.decode()

    @pytest.mark.parametrize("invalid_priority,expected_message", [
        ("3", "enter either 1"),
        ("0", "enter either 1"),
        ("abc", "enter either 1")
    ])
    def test_invalid_priority_inputs(self, client, test_phone, invalid_priority, expected_message):
        # Get to priority question
        client.post('/webhook', data={
            'Body': 'hi',
            'From': test_phone
        })
        client.post('/webhook', data={
            'Body': 'yes',
            'From': test_phone
        })
        # Invalid priority answer
        response = client.post('/webhook', data={
            'Body': invalid_priority,
            'From': test_phone
        })
        assert response.status_code == 200
        assert expected_message in response.data.decode() 