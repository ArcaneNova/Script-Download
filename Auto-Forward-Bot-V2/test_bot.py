#!/usr/bin/env python3
"""Quick bot connection test"""

import asyncio
import logging
from decouple import config
from pyrogram import Client, idle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test():
    API_ID = int(config("API_ID"))
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    
    logger.info(f"Testing with API_ID: {API_ID}")
    logger.info(f"Testing with API_HASH: {API_HASH[:20]}...")
    logger.info(f"Testing with BOT_TOKEN: {BOT_TOKEN[:30]}...")
    
    async with Client("test", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) as app:
        me = await app.get_me()
        logger.info(f"✓ Successfully connected as: @{me.username} (ID: {me.id})")
        logger.info(f"✓ Bot is ready!")

if __name__ == "__main__":
    asyncio.run(test())
