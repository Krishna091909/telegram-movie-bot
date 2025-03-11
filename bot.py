import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

# Bot Token
BOT_TOKEN = "7903162641:AAFJkO5g6QzJnxUYwpLcaYUvaIHzC84mxvk"
OWNER_ID = 7743703095  # Your Telegram User ID

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
    await update.message.reply_text("🎬 Send a movie name to get the download link.")

# Show available commands
async def help_command(update: Update, context: CallbackContext):
    commands = """
    ✅ Available Commands:
    /start - Start the bot
    /addmovie <movie_name> <file_id> - Add a movie (Owner Only)
    /removemovie <movie_name> - Remove a movie (Owner Only)
    /listmovies - Show all movies (Owner Only)
    """
    await update.message.reply_text(commands)

# Delete messages from the group after a delay
async def delete_message_later(message, delay=300):  # 5 minutes delay
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
        keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in matched_movies]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = await update.message.reply_text("🎬 Here is what I found for your query 👇:", reply_markup=reply_markup)
    else:
        msg = await update.message.reply_text("❌ Movie not found! Please check the spelling.")
    
    # Delete only in groups
    if update.message.chat.type in ["group", "supergroup"]:
        asyncio.create_task(delete_message_later(msg))  # Delete after 5 mins

# Handle movie selection and send file in DM
async def send_movie(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    movie_name = query.data
    movies = load_movies()
    file_id = movies.get(movie_name)

    if file_id:
        user_id = query.from_user.id  # Get the user ID
        await context.bot.send_document(chat_id=user_id, document=file_id, caption=f"🎬 {movie_name}")
        
        # Send "Check your DM" message in the group
        msg = await query.message.reply_text("📩 Check your DM for the movie file!\n⚠️ This message will be deleted in 5 minutes.")
        
        # Delete after 5 minutes
        if query.message.chat.type in ["group", "supergroup"]:
            asyncio.create_task(delete_message_later(msg))  # Delete "Check your DM" message
    else:
        await query.message.reply_text("❌ Movie not found.")

# Add a movie (Owner Only)
async def add_movie(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Usage: /addmovie <movie_name> <file_id>")
        return

    movie_name = " ".join(args[:-1])
    file_id = args[-1]
    movies = load_movies()
    movies[movie_name] = file_id
    save_movies(movies)

    await update.message.reply_text(f"✅ Movie '{movie_name}' added successfully!")

# Remove a movie (Owner Only)
async def remove_movie(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    movie_name = " ".join(context.args)
    movies = load_movies()

    if movie_name in movies:
        del movies[movie_name]
        save_movies(movies)
        await update.message.reply_text(f"🗑️ Movie '{movie_name}' removed successfully!")
    else:
        await update.message.reply_text("❌ Movie not found!")

# List all movies (Owner Only)
async def list_movies(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    movies = load_movies()
    if movies:
        movie_list = "\n".join(movies.keys())
        await update.message.reply_text(f"📜 Movies List:\n{movie_list}")
    else:
        await update.message.reply_text("❌ No movies available.")

# Get file ID (Owner Only)
async def get_file_id(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    document = update.message.document
    if document:
        await update.message.reply_text(f"File ID: `{document.file_id}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("Please send a movie file.")

# Bot setup
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("addmovie", add_movie))
    app.add_handler(CommandHandler("removemovie", remove_movie))
    app.add_handler(CommandHandler("listmovies", list_movies))
    app.add_handler(MessageHandler(filters.Document.ALL, get_file_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_movie_request))
    app.add_handler(CallbackQueryHandler(send_movie))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
