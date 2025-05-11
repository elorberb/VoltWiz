from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import os
import logging

from src.core.conversation import ConversationHandler
from src.core.calculator import ProviderCalculator

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize handlers
conversation_handler = ConversationHandler()
calculator = ProviderCalculator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the conversation and ask the first question."""
    user = update.effective_user
    welcome_message = (
        "אני VoltWiz – היועץ החכם שלך לבחירת תכנית החשמל הכי משתלמת! ⚡️\n"
        "בשיחה קצרה אני אכיר אותך ואמצא עבורך את החבילה שתעזור לך לחסוך הכי הרבה כסף, בדיוק לפי הסגנון שלך.\n\n"
        "בלי כאבי ראש, בלי אותיות קטנות – רק המלצה ברורה, פשוטה ומדויקת.\n"
        "יאללה, בוא נתחיל לחסוך 🙂"
    )
    await update.message.reply_text(welcome_message)
    
    # Reset any previous conversation
    conversation_handler.reset_conversation(str(user.id))
    # Get first question and buttons
    question, buttons = conversation_handler.get_next_question(str(user.id))
    keyboard = [[InlineKeyboardButton(btn, callback_data=btn) for btn in row] for row in buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'אני בוט שיעזור לך למצוא את ספק החשמל המתאים ביותר עבורך.\n'
        'אני אשאל אותך כמה שאלות קצרות כדי להבין את הצרכים שלך.\n\n'
        'הפקודות הזמינות:\n'
        '/start - התחל שיחה חדשה\n'
        '/help - הצג עזרה\n'
        '/reset - אפס את השיחה הנוכחית'
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset the conversation."""
    user = update.effective_user
    conversation_handler.reset_conversation(str(user.id))
    await update.message.reply_text('השיחה אופסה. בוא נתחיל מחדש!')
    question, buttons = conversation_handler.get_next_question(str(user.id))
    keyboard = [[InlineKeyboardButton(btn, callback_data=btn) for btn in row] for row in buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    answer = query.data

    # Process the answer
    response = conversation_handler.process_answer(user_id, answer)
    if response:
        await query.message.reply_text(response)
        return

    # If conversation is complete, get recommendation
    if conversation_handler.is_conversation_complete(user_id):
        user_data = conversation_handler.get_user_data(user_id)
        if user_data:
            # Create user preferences dictionary
            user_prefs = {
                "has_smart_meter": user_data.has_smart_meter,
                "discount_type": user_data.discount_type,
                "time_preference": user_data.time_preference,
                "vendor": user_data.vendor
            }

            # Get recommendation
            provider = calculator.get_recommendation(user_prefs)

            # Display recommendation
            if provider:
                recommendation = calculator.format_recommendation(provider, user_prefs)
                await query.message.reply_text(recommendation)
            else:
                await query.message.reply_text(
                    "מצטערים, לא מצאנו ספקים מתאימים לדרישות שלך."
                )
        else:
            await query.message.reply_text(
                "משהו השתבש. אנא נסה שוב עם /start"
            )
    else:
        # Get next question and buttons
        question, buttons = conversation_handler.get_next_question(user_id)
        if question:
            keyboard = [[InlineKeyboardButton(btn, callback_data=btn) for btn in row] for row in buttons]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(question, reply_markup=reply_markup)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a message to the user."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "מצטערים, אירעה שגיאה. אנא נסה שוב או השתמש ב /reset כדי להתחיל מחדש."
        )

def main() -> None:
    """Start the bot."""
    # Get token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

    # Create the application
    application = ApplicationBuilder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()