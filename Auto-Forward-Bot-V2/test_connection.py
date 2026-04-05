#!/usr/bin/env python3
"""
Test if bot can connect at all
"""
import asyncio
from decouple import config
from pyrogram import Client

async def test():
    API_ID = int(config("API_ID"))
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    
    print("Testing bot connection...")
    print(f"API_ID: {API_ID}")
    print(f"API_HASH: {API_HASH[:10]}...")
    print(f"BOT_TOKEN: {BOT_TOKEN[:10]}...")
    
    async with Client("test_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) as app:
        me = await app.get_me()
        print(f"\n✓ Connected successfully!")
        print(f"Bot: @{me.username}")
        print(f"Bot ID: {me.id}")
        print(f"Bot Name: {me.first_name}")

if __name__ == "__main__":
    asyncio.run(test())
