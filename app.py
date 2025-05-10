from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from conversation_handler import ConversationHandler
from calculator import ProviderCalculator
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
conversation_handler = ConversationHandler()
provider_calculator = ProviderCalculator()

@app.route("/webhook", methods=['POST'])
def webhook():
    # Get the message the user sent to the bot
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')

    # Create a Twilio response object
    resp = MessagingResponse()

    # Check if this is a new conversation
    if incoming_msg.lower() in ['hi', 'hello', 'start', 'help']:
        conversation_handler.reset_conversation(sender)
        msg = resp.message("Welcome to the Electricity Provider Recommendation Bot! Let's find the best plan for you.")
        msg = resp.message(conversation_handler.get_next_question(sender))
        return str(resp)

    # Process the conversation
    if not conversation_handler.is_conversation_complete(sender):
        next_question = conversation_handler.process_answer(sender, incoming_msg)
        if next_question:
            msg = resp.message(next_question)
        else:
            # Get the recommendation
            user_data = conversation_handler.get_user_data(sender)
            if user_data:
                # Create user preferences dictionary
                user_prefs = {
                    "has_smart_meter": user_data.has_smart_meter,
                    "priority": user_data.priority,
                    "min_discount_pct": user_data.min_discount_pct
                }

                # Add discount window if applicable
                if user_data.priority == "time_specific":
                    if user_data.discount_window:
                        user_prefs["discount_window"] = user_data.discount_window
                    else:
                        # Default to evening hours if not specified
                        user_prefs["discount_window"] = (18, 22)

                # Get recommendation
                provider = provider_calculator.get_recommendation(user_prefs)

                if provider:
                    recommendation = provider_calculator.format_recommendation(
                        provider,
                        user_prefs
                    )
                    msg = resp.message(recommendation)
                else:
                    msg = resp.message("Sorry, we couldn't find any suitable providers based on your requirements.")

                msg = resp.message("\nTo start over, just send 'hi' or 'start'.")
            else:
                msg = resp.message("Something went wrong. Please start over by sending 'hi'.")
    else:
        msg = resp.message("To start over, just send 'hi' or 'start'.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)