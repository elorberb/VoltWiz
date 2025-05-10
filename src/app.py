"""
Main application module for the VoltWiz application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app from the webhook module
from src.api.webhook import app

def run_app(host=None, port=None, debug=None):
    """
    Run the Flask application.
    
    Args:
        host: The host to run the app on (default: 0.0.0.0)
        port: The port to run the app on (default: 5000)
        debug: Whether to run the app in debug mode (default: True in development)
    """
    # Get configuration from environment variables if not provided
    if host is None:
        host = os.getenv("HOST", "0.0.0.0")
    
    if port is None:
        port = int(os.getenv("PORT", 5000))
    
    if debug is None:
        debug = os.getenv("FLASK_DEBUG", "1") == "1"
    
    # Run the app
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_app()
