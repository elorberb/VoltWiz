"""
Main application module for the VoltWiz application.
"""

import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_telegram_polling():
    """
    Run the Telegram bot in polling mode.
    """
    from src.api.telegram_bot import run_polling
    run_polling()

def run_telegram_webhook(webhook_url=None, port=None):
    """
    Run the Telegram bot in webhook mode.

    Args:
        webhook_url: The URL for the webhook (default: from environment)
        port: The port to run the webhook on (default: 5000)
    """
    from src.api.telegram_bot import run_webhook

    # Get configuration from environment variables if not provided
    if webhook_url is None:
        webhook_url = os.getenv("WEBHOOK_URL")
        if not webhook_url:
            raise ValueError("WEBHOOK_URL environment variable is not set")

    if port is None:
        port = int(os.getenv("PORT", 5000))

    run_webhook(webhook_url, port)

def run_app(mode="polling", webhook_url=None, port=None):
    """
    Run the application.

    Args:
        mode: The mode to run the application in (polling or webhook)
        webhook_url: The URL for the webhook (default: from environment)
        port: The port to run the webhook on (default: 5000)
    """
    if mode == "polling":
        run_telegram_polling()
    elif mode == "webhook":
        run_telegram_webhook(webhook_url, port)
    else:
        raise ValueError(f"Invalid mode: {mode}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the VoltWiz application")
    parser.add_argument(
        "--mode",
        choices=["polling", "webhook"],
        default="polling",
        help="The mode to run the application in (polling or webhook)"
    )
    parser.add_argument(
        "--webhook-url",
        help="The URL for the webhook (required for webhook mode)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="The port to run the webhook on (default: 5000)"
    )

    args = parser.parse_args()

    run_app(args.mode, args.webhook_url, args.port)
