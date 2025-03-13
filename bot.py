import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace this with your actual bot token
BOT_TOKEN = "7903162641:AAFJkO5g6QzJnxUYwpLcaYUvaIHzC84mxvk"

# Define the /start command handler
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! Welcome to the Movie Bot 🎬. Send a movie name to get a download link.")

# Define a handler for text messages
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    response = f"You searched for: {user_message}\nFetching movie link..."
    await update.message.reply_text(response)

# Define the main function to run the bot
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    await application.run_polling()

# Function to start the bot in a separate event loop
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

# Run the bot
if __name__ == "__main__":
    start_bot()
