#!/usr/bin/env python3
"""
Telegram Topic-Based Message Forwarder Bot
Complete implementation with menu, topic selection, and forwarding
"""

import asyncio
import logging
import sys
import re
import os
from datetime import datetime
from decouple import config
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import motor.motor_asyncio as motor
from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
try:
    API_ID = int(config("API_ID"))
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    DESTINATION_CHANNEL = config("DESTINATION_CHANNEL")
    DATABASE_URI = config("DATABASE", default=None)
except Exception as e:
    logger.error(f"Missing config: {e}")
    sys.exit(1)

# Pyrogram Client
app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# State
mongo_client = None
db = None
sessions = {}


# ===== DATABASE FUNCTIONS =====

async def init_db():
    """Initialize MongoDB connection."""
    global mongo_client, db
    if not DATABASE_URI:
        logger.warning("No DATABASE_URI - using memory only")
        return False
    
    try:
        mongo_client = motor.AsyncIOMotorClient(DATABASE_URI, serverSelectionTimeoutMS=5000)
        db = mongo_client.get_database()
        await mongo_client.admin.command('ping')
        logger.info("✓ MongoDB connected")
        return True
    except Exception as e:
        logger.warning(f"MongoDB unavailable: {e}")
        return False


# ===== UTILITY FUNCTIONS =====

def parse_channel(ch_str: str):
    """Parse channel URL/username to channel ID."""
    if not ch_str:
        return None
    
    ch_str = str(ch_str).strip()
    
    # Handle @username
    if ch_str.startswith("@"):
        return ch_str
    
    # Handle t.me/c/123456789 format
    if "t.me/c/" in ch_str:
        m = re.search(r't\.me/c/(\d+)', ch_str)
        if m:
            cid = int(m.group(1))
            return -100_000_000_000 - cid
    
    # Handle t.me/+invite format
    if "t.me/+" in ch_str:
        return ch_str
    
    # Try numeric ID
    try:
        return int(ch_str)
    except:
        return ch_str


def msg_type(msg: Message) -> str:
    """Get message type for display."""
    if msg.video:
        return "📹 Video"
    elif msg.document:
        return "📄 Document"
    elif msg.photo:
        return "🖼️ Photo"
    elif msg.audio:
        return "🎵 Audio"
    elif msg.voice:
        return "🎤 Voice"
    elif msg.video_note:
        return "🎥 VideoNote"
    else:
        return "📝 Text"


async def get_channel_topics(client: Client, ch_id) -> tuple:
    """Get channel and its topics."""
    try:
        chat = await client.get_chat(ch_id)
        
        topics = []
        seen = set()
        
        try:
            async for msg in client.get_chat_history(ch_id, limit=500):
                if hasattr(msg, 'topic_id') and msg.topic_id not in seen:
                    seen.add(msg.topic_id)
                    topics.append({
                        "id": msg.topic_id,
                        "title": f"Topic {msg.topic_id}"
                    })
        except:
            pass
        
        return chat, topics
    except Exception as e:
        logger.error(f"Error getting channel topics: {e}")
        return None, []


async def get_topic_messages(client: Client, ch_id, topic_id: int) -> list:
    """Get all messages from a specific topic in sequence."""
    messages = []
    try:
        async for msg in client.get_chat_history(ch_id, limit=10000):
            if hasattr(msg, 'topic_id'):
                if msg.topic_id == topic_id:
                    messages.append(msg)
            elif topic_id == 1:
                messages.append(msg)
        
        messages.reverse()  # Oldest first
        return messages
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return []


# ===== BOT COMMANDS =====

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    """Handle /start command - show main menu."""
    try:
        logger.info(f"✓ /START command received from user {message.from_user.id}")
        
        text = "🤖 **Telegram Topic Forwarder**\n\nSelect what you want to do:"
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Select Source Channel", callback_data="sel_ch")],
            [InlineKeyboardButton("📊 View Status", callback_data="stat")],
            [InlineKeyboardButton("❓ Help", callback_data="hlp")]
        ])
        
        await message.reply_text(text, reply_markup=kb)
        logger.info(f"✓ Menu sent to user {message.from_user.id}")
    except Exception as e:
        logger.error(f"ERROR in /start handler: {e}", exc_info=True)
        try:
            await message.reply_text(f"❌ Error: {str(e)[:100]}")
        except:
            pass


@app.on_callback_query()
async def callback_handler(client: Client, cq):
    """Handle all callback queries."""
    uid = cq.from_user.id
    data = cq.data
    
    logger.info(f"Callback: {data} from user {uid}")
    
    try:
        if data == "sel_ch":
            # Ask user to enter channel
            await cq.message.edit_text(
                "📥 **Send Channel URL:**\n\n"
                "Examples:\n"
                "`https://t.me/c/3895961049/`\n"
                "`https://t.me/+3CoEtU8yo0hhZGVh`\n"
                "`@channelname`",
                parse_mode="markdown"
            )
            if uid not in sessions:
                sessions[uid] = {}
            sessions[uid]["state"] = "waiting_channel"
        
        elif data == "stat":
            # Show status
            sess = sessions.get(uid, {})
            status_text = (
                f"**Status**\n\n"
                f"Channel: `{sess.get('channel', 'None')}`\n"
                f"Total Forwarded: `{sess.get('total_fwd', 0)}`\n"
                f"Failed: `{sess.get('failed', 0)}`"
            )
            await cq.message.edit_text(status_text, parse_mode="markdown")
        
        elif data == "hlp":
            # Show help
            help_text = (
                "**How to Use:**\n\n"
                "1️⃣ Click 'Select Source Channel'\n"
                "2️⃣ Send channel URL or invite link\n"
                "3️⃣ Select a topic from the list\n"
                "4️⃣ Bot will forward all messages in sequence\n"
                "5️⃣ Watch progress updates\n\n"
                "**Destination:** @gatearshadbackup"
            )
            await cq.message.edit_text(help_text, parse_mode="markdown")
        
        elif data.startswith("topic_"):
            # Handle topic selection and forward
            topic_id = int(data.split("_")[1])
            await forward_messages_from_topic(client, cq, uid, topic_id)
        
        await cq.answer()
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await cq.answer(f"Error: {e}", show_alert=True)


@app.on_message(filters.text & filters.private & filters.incoming)
async def text_handler(client: Client, message: Message):
    """Handle text messages (channel URLs, etc.)."""
    uid = message.from_user.id
    text = message.text.strip()
    
    # Ignore commands
    if text.startswith("/"):
        return
    
    logger.info(f"Text from user {uid}")
    
    if uid not in sessions:
        sessions[uid] = {}
    
    sess = sessions[uid]
    
    # User sending channel URL
    if sess.get("state") == "waiting_channel":
        try:
            # Parse channel
            ch_id = parse_channel(text)
            
            # Show loading status
            status_msg = await message.reply_text("⏳ Checking channel...")
            
            try:
                # Get channel and topics
                chat, topics = await get_channel_topics(client, ch_id)
                
                if not chat:
                    await status_msg.edit_text(
                        "❌ Cannot access channel.\n\n"
                        "Make sure:\n"
                        "• Bot is a member of the channel\n"
                        "• Channel URL is correct"
                    )
                    return
                
                # Save channel info
                sessions[uid] = {
                    "state": "idle",
                    "channel": text,
                    "channel_id": ch_id,
                    "title": chat.title,
                    "total_fwd": 0,
                    "failed": 0
                }
                
                if not topics:
                    await status_msg.edit_text(
                        f"❌ No topics found in {chat.title}\n\n"
                        "This channel either:\n"
                        "• Doesn't have topics enabled\n"
                        "• Topics are not accessible"
                    )
                    return
                
                # Show topics as buttons
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"📌 Topic {t['id']}", callback_data=f"topic_{t['id']}")]
                    for t in topics
                ])
                
                await status_msg.edit_text(
                    f"✅ **Connected to {chat.title}**\n\n"
                    f"Found {len(topics)} topic(s)\n\n"
                    f"Select a topic to forward all its messages:",
                    reply_markup=kb
                )
                
            except Exception as e:
                logger.error(f"Channel access error: {e}")
                await status_msg.edit_text(f"❌ Error: {str(e)[:100]}")
        
        except Exception as e:
            logger.error(f"Text handler error: {e}")
            await message.reply_text(f"❌ Error: {str(e)[:100]}")
    
    else:
        # User not in expected state
        await message.reply_text("Use /start to begin")


async def forward_messages_from_topic(client: Client, cq, uid: int, topic_id: int):
    """Forward all messages from selected topic."""
    try:
        sess = sessions.get(uid, {})
        ch_str = sess.get("channel")
        ch_id = sess.get("channel_id")
        
        if not ch_str:
            await cq.answer("No channel selected!", show_alert=True)
            return
        
        # Parse destination
        dest_id = parse_channel(DESTINATION_CHANNEL)
        
        # Get messages from topic
        status_msg = await cq.message.edit_text(
            f"⏳ **Fetching messages from Topic {topic_id}...**"
        )
        
        messages = await get_topic_messages(client, ch_id, topic_id)
        
        if not messages:
            await status_msg.edit_text(f"❌ No messages found in topic {topic_id}")
            return
        
        total = len(messages)
        forwarded = 0
        failed = 0
        
        # Initial status
        await status_msg.edit_text(
            f"📤 **Starting to forward {total} messages...**\n\n"
            f"Topic: `{topic_id}`\n"
            f"Progress: `0/{total}` (0%)"
        )
        
        # Forward each message
        for idx, msg in enumerate(messages, 1):
            try:
                # Forward message
                await client.forward_messages(
                    chat_id=dest_id,
                    from_chat_id=ch_id,
                    message_ids=msg.id
                )
                forwarded += 1
                
                # Update progress every 5 messages or on last message
                if idx % 5 == 0 or idx == total:
                    pct = int((idx / total) * 100)
                    await status_msg.edit_text(
                        f"📤 **Forwarding Messages**\n\n"
                        f"Topic: `{topic_id}`\n"
                        f"Progress: `{idx}/{total}` ({pct}%)\n"
                        f"Success: `{forwarded}` ✓\n"
                        f"Failed: `{failed}` ✗"
                    )
                
                # Rate limiting
                await asyncio.sleep(0.3)
                
            except FloodWait as e:
                # Rate limit hit - wait
                await asyncio.sleep(min(e.value, 30))
                
            except Exception as e:
                logger.warning(f"Message forward error: {e}")
                failed += 1
                await asyncio.sleep(1)
        
        # Update session
        sessions[uid]["total_fwd"] = sessions[uid].get("total_fwd", 0) + forwarded
        sessions[uid]["failed"] = sessions[uid].get("failed", 0) + failed
        
        # Final summary
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Forward Another Topic", callback_data="sel_ch")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="stat")]
        ])
        
        await status_msg.edit_text(
            f"✅ **Forwarding Complete!**\n\n"
            f"Topic: `{topic_id}`\n"
            f"Total Messages: `{total}`\n"
            f"Successfully Forwarded: `{forwarded}` ✓\n"
            f"Failed: `{failed}` ✗\n\n"
            f"All messages forwarded to @gatearshadbackup in exact sequence!",
            reply_markup=kb
        )
        
    except Exception as e:
        logger.error(f"Forward error: {e}")
        await cq.answer(f"Error: {str(e)[:100]}", show_alert=True)


# ===== HTTP SERVER FOR RENDER HEALTH CHECK =====

async def start_http_server():
    """Start aiohttp web server for health checks."""
    port = int(os.getenv("PORT", 8000))
    
    async def health_check(request):
        return web.Response(text="OK", status=200)
    
    web_app = web.Application()
    web_app.router.add_get("/", health_check)
    web_app.router.add_get("/health", health_check)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"✓ HTTP server started on port {port}")


# ===== MAIN =====

async def main():
    """Start the bot."""
    logger.info("=" * 70)
    logger.info("Telegram Topic-Based Message Forwarder Bot")
    logger.info("=" * 70)
    logger.info(f"Bot Token: {BOT_TOKEN[:20]}...")
    logger.info(f"API ID: {API_ID}")
    
    # Initialize database
    await init_db()
    
    # Start HTTP server for Render health checks (non-blocking)
    try:
        asyncio.create_task(start_http_server())
        logger.info("✓ HTTP server task created")
    except Exception as e:
        logger.warning(f"HTTP server startup warning: {e}")
    
    try:
        logger.info("Starting Pyrogram client...")
        async with app:
            logger.info("✓✓✓ PYROGRAM CLIENT CONNECTED ✓✓✓")
            
            # Verify bot identity
            me = await app.get_me()
            logger.info(f"✓ Bot Username: @{me.username}")
            logger.info(f"✓ Bot ID: {me.id}")
            
            # Verify destination channel
            logger.info(f"✓ Destination Channel: {DESTINATION_CHANNEL}")
            
            # Log all registered handlers
            logger.info(f"✓ Total Handlers Registered: {len(app._handler_groups)}")
            logger.info("  - Handler 1: /start command (private messages)")
            logger.info("  - Handler 2: Callback queries (buttons)")
            logger.info("  - Handler 3: Text messages (channel URLs)")
            
            logger.info("=" * 70)
            logger.info("✓✓✓ BOT IS RUNNING AND READY ✓✓✓")
            logger.info("Waiting for /start commands in private messages...")
            logger.info("=" * 70)
            
            # Start polling
            await idle()
            
    except KeyboardInterrupt:
        logger.info("\n✓ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {e}", exc_info=True)
        raise
    finally:
        if mongo_client:
            try:
                mongo_client.close()
                logger.info("✓ Database connection closed")
            except:
                pass


if __name__ == "__main__":
    asyncio.run(main())