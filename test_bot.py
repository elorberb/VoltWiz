#!/usr/bin/env python
"""
Test script for the Telegram bot.
This script checks if the bot token is valid and can connect to the Telegram API.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_telegram_token():
    """Test if the Telegram bot token is valid."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is not set.")
        print("Please create a .env file with your Telegram bot token.")
        return False
    
    # Test the token by making a request to the Telegram API
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("ok"):
            bot_info = data.get("result", {})
            bot_name = bot_info.get("first_name", "Unknown")
            bot_username = bot_info.get("username", "Unknown")
            
            print(f"✅ Connection successful!")
            print(f"Bot Name: {bot_name}")
            print(f"Bot Username: @{bot_username}")
            print("\nYour bot is ready to use. Run 'python run_bot.py' to start the bot.")
            return True
        else:
            print(f"❌ Error: {data.get('description', 'Unknown error')}")
            return False
    
    except requests.RequestException as e:
        print(f"❌ Error connecting to Telegram API: {e}")
        return False

if __name__ == "__main__":
    print("Testing Telegram bot connection...")
    if not test_telegram_token():
        sys.exit(1)
