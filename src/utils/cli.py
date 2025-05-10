from core.calculator import ProviderCalculator

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
    Run the CLI interface.
    """
    # Initialize the calculator
    calculator = ProviderCalculator()
    
    # Get user preferences
    print("Welcome to the Electricity Provider Recommendation Bot!")
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
