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

def start_server():
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000
    app.run(host='0.0.0.0', port=port)

# Load movies from JSON file
def load_movies():
    try:
        with open("movies.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save movies to JSON file
def save_movies(movies):
    with open("movies.json", "w") as file:
        json.dump(movies, file, indent=4)

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("\ud83c\udfae Send a movie name to get the download link.")

# Help command
async def help_command(update: Update, context: CallbackContext):
    commands = """
    \u2705 Available Commands:
    /start - Start the bot
    /addmovie <movie_name> <file_id> <file_size> <file_name> - Add a movie (Owner Only)
    /removemovie <movie_name> - Remove a movie (Owner Only)
    /listmovies - Show all movies (Owner Only)
    /getid - Get File ID, Name & Size (Owner Only)
    """
    await update.message.reply_text(commands)

# Delete messages after a delay
async def delete_message_later(message, delay=300):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Failed to delete message: {e}")

# Handle movie search in groups
async def handle_movie_request(update: Update, context: CallbackContext):
    movies = load_movies()
    movie_name = update.message.text.lower()
    matched_movies = [key for key in movies.keys() if movie_name in key.lower()]

    if matched_movies:
        keyboard = [
            [InlineKeyboardButton(f"{movies[name]['file_size']} | {movies[name]['file_name']}", callback_data=name)]
            for name in matched_movies
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = await update.message.reply_text("\ud83c\udfae Here is what I found for your query \ud83d\udc47:", reply_markup=reply_markup)
    else:
        msg = await update.message.reply_text("\u274c Movie not found! Please check the spelling.")

    if update.message.chat.type in ["group", "supergroup"]:
        asyncio.create_task(delete_message_later(msg))

# Handle movie selection and send file in DM
async def send_movie(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    movie_name = query.data
    movies = load_movies()
    movie_data = movies.get(movie_name)

    if movie_data:
        user_id = query.from_user.id  
        file_id = movie_data["file_id"]
        file_size = movie_data["file_size"]
        file_name = movie_data["file_name"]

        await context.bot.send_document(
            chat_id=user_id, 
            document=file_id, 
            caption=f"\ud83c\udfae *{file_name}*\n\ud83d\udce6 *Size:* {file_size}",
            parse_mode="Markdown"
        )
        
        msg = await query.message.reply_text("\ud83d\udce9 Check your DM for the movie file!\n\u26a0\ufe0f This message will be deleted in 5 minutes.")
        
        if query.message.chat.type in ["group", "supergroup"]:
            asyncio.create_task(delete_message_later(msg))
    else:
        await query.message.reply_text("\u274c Movie not found.")

# Run the bot
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_movie_request))
    app.add_handler(CallbackQueryHandler(send_movie))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    threading.Thread(target=start_server).start()
