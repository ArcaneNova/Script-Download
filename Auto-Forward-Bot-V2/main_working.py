#!/usr/bin/env python3
"""
Minimal working Telegram bot - guaranteed to respond to /start
"""

import asyncio
import logging
import sys
from decouple import config
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('bot.log')]
)
logger = logging.getLogger(__name__)

# Config
API_ID = int(config("API_ID"))
API_HASH = config("API_HASH")
BOT_TOKEN = config("BOT_TOKEN")
DESTINATION_CHANNEL = config("DESTINATION_CHANNEL")

# Bot
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== HANDLERS =====

@app.on_message(filters.command("start"))
async def start(client, message):
    """Respond to /start - THIS MUST WORK"""
    try:
        logger.info(f"✓✓✓ RECEIVED /start FROM {message.from_user.id} ✓✓✓")
        
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Select Channel", callback_data="sel_ch")]])
        await message.reply_text("🤖 Bot is working!\n\nSelect an option:", reply_markup=kb)
        logger.info("✓ Reply sent successfully")
    except Exception as e:
        logger.error(f"ERROR in /start: {e}", exc_info=True)

@app.on_callback_query()
async def callback(client, query):
    """Handle callbacks"""
    try:
        logger.info(f"Callback: {query.data}")
        await query.answer("Got it!", show_alert=False)
    except Exception as e:
        logger.error(f"Callback error: {e}")

# ===== MAIN =====

async def main():
    logger.info("="*70)
    logger.info("TELEGRAM BOT STARTING")
    logger.info("="*70)
    
    try:
        async with app:
            me = await app.get_me()
            logger.info(f"✓ Bot: @{me.username} (ID: {me.id})")
            logger.info(f"✓ Destination: {DESTINATION_CHANNEL}")
            logger.info("="*70)
            logger.info("✓✓✓ BOT IS READY - AWAITING MESSAGES ✓✓✓")
            logger.info("Send /start command now")
            logger.info("="*70)
            
            await idle()
    except Exception as e:
        logger.error(f"FATAL: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
