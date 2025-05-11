"""
CLI interface for the VoltWiz application.
"""

from src.core.calculator import ProviderCalculator
from src.core.conversation import ConversationHandler

def get_user_preferences():
    """
    Prompt the user for their electricity-plan preferences,
    and return a dict of their choices.
    """
    prefs = {}

    # 1. Smart-meter requirement
    ans = input("Do you have (or can install) a smart meter? [y/n]: ").strip().lower()
    prefs["has_smart_meter"] = (ans == "y")

    # 2. Priority: max discount vs. full-day coverage
    print("What's most important to you?")
    print("  1) Highest % discount")
    print("  2) Discount during specific hours")
    choice = input("Enter 1 or 2: ").strip()
    prefs["priority"] = "max_discount" if choice == "1" else "time_specific"

    # 3. If time-specific, ask for preferred window
    if prefs["priority"] == "time_specific":
        start = input("  Discount start hour (0–23): ").strip()
        end   = input("  Discount end   hour (0–23): ").strip()
        prefs["discount_window"] = (int(start), int(end))

    # 4. Optional: minimum discount threshold
    thresh = input("Minimum acceptable discount % (e.g. 10): ").strip()
    prefs["min_discount_pct"] = float(thresh) if thresh else 0.0

    return prefs

def run_cli_conversation():
    """
    Run the CLI interface using the conversation handler.
    """
    handler = ConversationHandler()
    calculator = ProviderCalculator()
    user_id = "cli_user"

    print("Welcome to the Electricity Provider Recommendation CLI")
    print("-----------------------------------------------------")

    # Reset any previous conversation
    handler.reset_conversation(user_id)

    # Run through the conversation
    while not handler.is_conversation_complete(user_id):
        question = handler.get_next_question(user_id)
        print(question)
        answer = input("> ")
        response = handler.process_answer(user_id, answer)
        if response:
            print(response)

    # Get the recommendation
    user_data = handler.get_user_data(user_id)
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
        provider = calculator.get_recommendation(user_prefs)

        # Display recommendation
        print("\nBased on your preferences:")
        if provider:
            recommendation = calculator.format_recommendation(provider, user_prefs)
            print(recommendation)
        else:
            print("Sorry, we couldn't find any suitable providers based on your requirements.")
    else:
        print("Something went wrong. Please try again.")

def run_cli_direct():
    """
    Run the CLI interface using direct preference input.
    """
    calculator = ProviderCalculator()

    # Get user preferences
    print("Welcome to the Electricity Provider Recommendation CLI")
    print("-----------------------------------------------------")
    user_prefs = get_user_preferences()

    # Get recommendation
    provider = calculator.get_recommendation(user_prefs)

    # Display recommendation
    print("\nBased on your preferences:")
    if provider:
        recommendation = calculator.format_recommendation(provider, user_prefs)
        print(recommendation)
    else:
        print("Sorry, we couldn't find any suitable providers based on your requirements.")

def run_cli():
    """
    Run the CLI interface, asking the user which mode to use.
    """
    print("Welcome to the Electricity Provider Recommendation CLI")
    print("-----------------------------------------------------")
    print("How would you like to provide your preferences?")
    print("  1) Answer questions in a conversation")
    print("  2) Provide all preferences at once")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        run_cli_conversation()
    else:
        run_cli_direct()

if __name__ == "__main__":
    run_cli()
