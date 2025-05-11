#!/usr/bin/env python
"""
Helper script to set up ngrok for testing the Telegram bot.
This script assumes you have ngrok installed and available in your PATH.
"""

import os
import sys
import subprocess
import json
import webbrowser
from urllib.request import urlopen
from urllib.error import URLError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_ngrok_installed():
    """Check if ngrok is installed and available in PATH."""
    try:
        subprocess.run(["ngrok", "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def get_ngrok_url():
    """Get the public URL from ngrok API."""
    try:
        response = urlopen("http://localhost:4040/api/tunnels")
        data = json.loads(response.read().decode())
        return next((tunnel["public_url"] for tunnel in data["tunnels"] 
                    if tunnel["proto"] == "https"), None)
    except (URLError, json.JSONDecodeError, KeyError, StopIteration):
        return None

def main():
    # Check if ngrok is installed
    if not check_ngrok_installed():
        print("Error: ngrok is not installed or not in your PATH.")
        print("Please install ngrok from https://ngrok.com/download")
        sys.exit(1)
    
    # Get the port from environment or use default
    port = os.getenv("PORT", "5000")
    
    # Start ngrok in a subprocess
    print(f"Starting ngrok tunnel to port {port}...")
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", port],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a moment for ngrok to start
    import time
    time.sleep(2)
    
    # Get the public URL
    public_url = get_ngrok_url()
    if not public_url:
        print("Error: Could not get ngrok public URL.")
        print("Make sure ngrok is running correctly.")
        ngrok_process.terminate()
        sys.exit(1)
    
    # Print the webhook URL
    webhook_url = public_url
    print("\n" + "=" * 60)
    print(f"Ngrok tunnel established!")
    print(f"Public URL: {public_url}")
    print(f"Webhook URL: {webhook_url}")
    print("=" * 60)
    print("\nUse this URL in your .env file or when running the bot:")
    print(f"WEBHOOK_URL={webhook_url}")
    print("\nOr run the bot with:")
    print(f"python run.py telegram --mode webhook --webhook-url {webhook_url}")
    print("\nPress Ctrl+C to stop the ngrok tunnel when you're done.")
    
    # Open the ngrok web interface
    webbrowser.open("http://localhost:4040")
    
    try:
        # Keep the script running until interrupted
        ngrok_process.wait()
    except KeyboardInterrupt:
        print("\nStopping ngrok tunnel...")
        ngrok_process.terminate()
        print("Tunnel closed.")

if __name__ == "__main__":
    main()
