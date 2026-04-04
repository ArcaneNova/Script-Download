#!/usr/bin/env python3
"""
Simple Telegram message forwarder using Pyrogram.
Forwards all messages from a private channel to a public channel automatically.
"""
import asyncio
import logging
from decouple import config
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load config
API_ID = int(config("API_ID"))
API_HASH = config("API_HASH")
BOT_TOKEN = config("BOT_TOKEN")
SOURCE_CHANNEL = config("SOURCE_CHANNEL")
DESTINATION_CHANNEL = config("DESTINATION_CHANNEL")

# Initialize client
app = Client(
    "autoforward_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=4
)


def parse_channel_id(channel_str):
    """Parse channel ID from URL, username, or integer."""
    if not channel_str:
        return None
    
    # Handle t.me URLs
    if "t.me/" in channel_str:
        import re
        match = re.search(r'(?:https?://)?t\.me/\+?([a-zA-Z0-9_-]+)', channel_str)
        if match:
            part = match.group(1)
            # Check if numeric
            try:
                return int(part)
            except ValueError:
                return f"@{part}"
    
    # Handle @username
    if channel_str.startswith("@"):
        return channel_str
    
    # Handle numeric IDs
    try:
        return int(channel_str)
    except ValueError:
        return channel_str


@app.on_message(filters.chat(parse_channel_id(SOURCE_CHANNEL)))
async def forward_message(client, message):
    """Forward messages from source to destination."""
    try:
        if message.service:
            logger.debug(f"Skipping service message")
            return
        
        dest_id = parse_channel_id(DESTINATION_CHANNEL)
        
        await client.forward_messages(
            chat_id=dest_id,
            from_chat_id=parse_channel_id(SOURCE_CHANNEL),
            message_ids=message.id
        )
        logger.info(f"✓ Forwarded message {message.id}")
        
    except FloodWait as e:
        logger.warning(f"Flood wait for {e.value} seconds, retrying...")
        await asyncio.sleep(e.value)
        await client.forward_messages(
            chat_id=parse_channel_id(DESTINATION_CHANNEL),
            from_chat_id=parse_channel_id(SOURCE_CHANNEL),
            message_ids=message.id
        )
        logger.info(f"✓ Forwarded message {message.id} after flood wait")
        
    except Exception as e:
        logger.error(f"✗ Failed to forward message {message.id}: {e}")


async def main():
    logger.info("Starting Auto-Forward Bot...")
    logger.info(f"Source: {SOURCE_CHANNEL}")
    logger.info(f"Destination: {DESTINATION_CHANNEL}")
    
    async with app:
        me = await app.get_me()
        logger.info(f"✓ Connected as bot: @{me.username}")
        
        await app.idle()


if __name__ == "__main__":
    try:
        app.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
