import logging
import asyncio
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive
import main  # Importing your game bot logic
from xC4 import Emote_k, SEndPacKeT  # Importing helper functions
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
BOT_TOKEN = "7105964423:AAFawh1AnTGVOiw0k-YBNqN0aZiAuHaWfO4"  # Aapka Token

# Load emotes
def load_emotes():
    try:
        with open('emotes.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading emotes: {e}")
        return []

emotes_data = load_emotes()

# --- HELPER FUNCTIONS ---
def get_emote_id_by_number(number):
    for emote in emotes_data:
        if emote['Number'] == str(number):
            return int(emote['Id'])
    return None

# --- COMMAND HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 **Free Fire Bot Connected!** 🔥\n\n"
        "Use /help to see commands.\n"
        "Status: Checking game connection..."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 **BOT COMMANDS**

💃 **Emotes:**
`/c [uid] [emote_number]` - Send emote by number (1-20)
`/e [uid] [emote_id]` - Send emote by ID
`/fast [uid] [emote_id]` - Spam emote 25x

🛠 **Status:**
`/status` - Check if bot is online in game
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if main.online_writer is None:
        await update.message.reply_text("❌ **Bot Offline** in Game. Trying to reconnect...")
    else:
        await update.message.reply_text(f"✅ **Bot Online**\nRegion: {getattr(main, 'region', 'Unknown')}\nTarget UID: {getattr(main, 'TarGeT', 'Unknown')}")

async def send_emote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Command: /c uid number
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/c [uid] [number]`")
        return

    # Check Connection
    if main.online_writer is None or not hasattr(main, 'key'):
        await update.message.reply_text("⚠️ Bot is not connected to the game server yet. Please wait.")
        return

    try:
        target_uid = int(context.args[0])
        emote_num = context.args[1]
        
        emote_id = get_emote_id_by_number(emote_num)
        
        if not emote_id:
            await update.message.reply_text("❌ Invalid Emote Number!")
            return

        # Send Packet using variables from main.py
        packet = await Emote_k(target_uid, emote_id, main.key, main.iv, main.region)
        await SEndPacKeT(main.whisper_writer, main.online_writer, 'OnLine', packet)
        
        await update.message.reply_text(f"✅ Sent Emote #{emote_num} to {target_uid}")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def spam_fast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Command: /fast uid emote_id
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/fast [uid] [emote_id]`")
        return

    if main.online_writer is None:
        await update.message.reply_text("⚠️ Bot Offline")
        return

    try:
        uid = int(context.args[0])
        emote_id = int(context.args[1])
        
        await update.message.reply_text(f"🚀 Spamming Emote {emote_id} to {uid}...")
        
        # Run spam in background
        asyncio.create_task(main.fast_emote_spam([str(uid)], str(emote_id), main.key, main.iv, main.region))
        
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# --- MAIN EXECUTION ---

async def run_game_bot():
    """Starts the game bot logic in the background"""
    while True:
        try:
            print("🚀 Starting Game Logic...")
            await main.MaiiiinE()
        except Exception as e:
            print(f"Game Logic Error: {e}")
        await asyncio.sleep(5)

def main_loop():
    """Main entry point"""
    # 1. Start Keep Alive Web Server (For Render)
    keep_alive()

    # 2. Setup Telegram Bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("c", send_emote_command))
    application.add_handler(CommandHandler("fast", spam_fast))

    # 3. Get Async Event Loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 4. Schedule Game Bot Task
    loop.create_task(run_game_bot())

    # 5. Run Telegram Bot (Polling)
    print("🤖 Telegram Bot Started...")
    
    # We use run_polling with stop_signals=None to allow background tasks
    application.run_polling(loop=loop)

if __name__ == '__main__':
    main_loop()