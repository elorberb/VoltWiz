# VoltWiz - Electricity Provider Recommendation Bot

A Telegram bot that helps users find the best electricity provider based on their needs and usage patterns. The bot interacts with users, collects their preferences, and provides personalized recommendations.

## Features

- Interactive conversation flow via Telegram
- Smart provider matching based on user requirements
- Preference-based recommendations (highest discount or time-specific discount)
- Detailed recommendation with plan details and next steps
- Support for both polling and webhook modes
- CLI interface for testing without Telegram

## How It Works

1. **User Initiates Conversation**: The user sends a `/start` command to the Telegram bot.
2. **Bot Asks Questions**: The bot asks a series of questions about the user's preferences:
   - Whether they have a smart meter
   - What's most important to them (highest discount or time-specific discount)
   - If time-specific, what hours they prefer
   - Minimum acceptable discount percentage
3. **Recommendation Calculation**: Based on the answers, the bot:
   - Filters out ineligible plans
   - Scores plans based on the user's priority (highest discount or time-specific)
   - Identifies the best plan
4. **Recommendation Delivery**: The bot sends a detailed recommendation including:
   - The recommended provider name
   - Plan details (discount percentage, hours, smart meter requirement)
   - Why this plan was chosen
   - Next steps for the user

## Installation
```bash
pip install uv
```

```bash
uv venv
```

```bash
# For Windows
.venv\Scripts\activate

# For macOSon Linux
source .venv/bin/activate
```

```bash
uv pip install -r requirements.txt
```

## Setting Up Telegram Bot

1. **Create a Telegram Bot**:
   - Open Telegram and search for the "BotFather" (@BotFather)
   - Send the `/newbot` command and follow the instructions
   - BotFather will give you a token for your new bot
   - Copy this token to your `.env` file as `TELEGRAM_BOT_TOKEN`

2. **Configure Environment Variables**:
   - Create a `.env` file in the project root
   - Add your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

3. **Test Your Bot Setup**:
   - Run the test script to verify your bot token is working:
   ```bash
   python test_bot.py
   ```
   - If successful, you'll see your bot's information
   - If there's an error, check your token and try again

## Usage

### Running the Telegram Bot

The simplest way to run the bot is in polling mode:

```bash
python run_bot.py
```

This will start the bot and it will respond to messages sent to it on Telegram.

### Available Commands

Once the bot is running, you can interact with it using these commands:

- `/start` - Start the bot and get a welcome message
- `/help` - Show help information
- `/recommend` - Get a simple provider recommendation

### Testing Without Telegram

You can also test the recommendation system without using Telegram:

```bash
python -m src.utils.cli
```



## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
