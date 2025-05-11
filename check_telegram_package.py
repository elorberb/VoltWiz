#!/usr/bin/env python
"""
Check if the python-telegram-bot package is installed correctly.
"""

import sys

def check_package():
    """Check if the python-telegram-bot package is installed correctly."""
    print("Checking python-telegram-bot package...")
    
    try:
        import telegram
        print(f"✅ telegram package is installed (version: {telegram.__version__})")
    except ImportError:
        print("❌ telegram package is not installed")
        return False
    
    try:
        from telegram.ext import Application
        print("✅ telegram.ext.Application is available")
    except ImportError:
        print("❌ telegram.ext.Application is not available")
        print("This might indicate an incomplete installation or version mismatch")
        return False
    
    print("\nAll checks passed! The python-telegram-bot package is installed correctly.")
    return True

if __name__ == "__main__":
    if not check_package():
        print("\nTo fix this issue, try reinstalling the package:")
        print("pip install python-telegram-bot==20.7 --upgrade")
        sys.exit(1)
