#!/usr/bin/env python3
"""
Telegram Auto-Forward Bot
Automatically forwards all messages from SOURCE_CHANNEL to DESTINATION_CHANNEL.
No manual commands needed - just set environment variables and run.
"""
import asyncio
import logging
import sys
from decouple import config
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('forward_bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Load configuration from environment
try:
    API_ID = int(config("API_ID"))
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    SOURCE_CHANNEL = config("SOURCE_CHANNEL")
    DESTINATION_CHANNEL = config("DESTINATION_CHANNEL")
    DATABASE_URI = config("DATABASE", default=None)
except Exception as e:
    logger.error(f"Missing configuration: {e}")
    sys.exit(1)

logger.info(f"Config loaded:")
logger.info(f"  Source: {SOURCE_CHANNEL}")
logger.info(f"  Destination: {DESTINATION_CHANNEL}")

# Initialize Pyrogram client
app = Client(
    "telegram_forwarder",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=4
)


def parse_channel_id(channel_str):
    """Parse channel ID from URL, username, or numeric ID."""
    if not channel_str:
        return None
    
    channel_str = str(channel_str).strip()
    
    # Handle @username format
    if channel_str.startswith("@"):
        logger.info(f"Parsed username: {channel_str}")
        return channel_str
    
    # Handle t.me/c/123456789 (private channel)
    if "t.me/c/" in channel_str:
        import re
        match = re.search(r't\.me/c/(\d+)', channel_str)
        if match:
            channel_id = int(match.group(1))
            # Pyrogram format for private channels: -100{channel_id}
            formatted_id = -100_000_000_000 - channel_id
            logger.info(f"Parsed private channel URL: {channel_str} -> {formatted_id}")
            return formatted_id
    
    # Handle t.me/+invite (private channel invite)
    if "t.me/+" in channel_str:
        logger.info(f"Detected private channel invite link: {channel_str}")
        # For invite links, we need to use the channel object or resolve it
        return channel_str
    
    # Handle numeric ID
    try:
        channel_id = int(channel_str)
        logger.info(f"Parsed numeric ID: {channel_id}")
        return channel_id
    except ValueError:
        logger.warning(f"Could not parse channel: {channel_str}, using as-is")
        return channel_str


# Parse channel IDs
source_id = parse_channel_id(SOURCE_CHANNEL)
dest_id = parse_channel_id(DESTINATION_CHANNEL)

logger.info(f"Resolved IDs:")
logger.info(f"  Source ID: {source_id}")
logger.info(f"  Destination ID: {dest_id}")


@app.on_message(filters.chat(source_id) & ~filters.service)
async def forward_message(client, message):
    """Forward message from source to destination."""
    try:
        await client.forward_messages(
            chat_id=dest_id,
            from_chat_id=source_id,
            message_ids=message.id
        )
        logger.info(f"✓ Forwarded message {message.id}")
        
    except FloodWait as e:
        logger.warning(f"⏱ Flood wait: sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
        try:
            await client.forward_messages(
                chat_id=dest_id,
                from_chat_id=source_id,
                message_ids=message.id
            )
            logger.info(f"✓ Forwarded message {message.id} (after flood wait)")
        except Exception as inner_e:
            logger.error(f"✗ Failed to forward after flood wait: {inner_e}")
            
    except Exception as e:
        logger.error(f"✗ Failed to forward message {message.id}: {e}")


async def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Telegram Auto-Forward Bot Starting")
    logger.info("=" * 60)
    
    try:
        async with app:
            me = await app.get_me()
            logger.info(f"✓ Connected as: @{me.username} (ID: {me.id})")
            logger.info(f"✓ Listening for messages from source channel...")
            logger.info(f"✓ Will auto-forward to destination channel...")
            logger.info("")
            logger.info("Bot is running. Press Ctrl+C to stop.")
            logger.info("=" * 60)
            
            await app.idle()
            
    except KeyboardInterrupt:
        logger.info("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        app.run(main())
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        sys.exit(1)
