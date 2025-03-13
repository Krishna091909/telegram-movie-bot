import json
import asyncio
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

# Bot Token and Owner ID
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Load from Render environment variable
OWNER_ID = 7743703095  # Your Telegram User ID

# Flask App for Render Web Service
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addmovie", add_movie))
    application.add_handler(CommandHandler("removemovie", remove_movie))
    application.add_handler(CommandHandler("listmovies", list_movies))
    application.add_handler(CommandHandler("getid", get_file_id))
    application.add_handler(MessageHandler(filters.Document.ALL, get_file_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_movie_request))
    application.add_handler(CallbackQueryHandler(send_movie))
    
    print("Bot is running...")
    await application.run_polling()

async def main():
    loop = asyncio.get_event_loop()
    
    # Run Flask server in a thread
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000))), daemon=True)
    flask_thread.start()
    
    # Run Telegram bot
    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())
