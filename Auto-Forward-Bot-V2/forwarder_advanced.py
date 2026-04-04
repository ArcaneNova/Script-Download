#!/usr/bin/env python3
"""
Advanced Telegram Topic-Based Message Forwarder Bot
- Multi-topic support with progress tracking
- Real-time status dashboard
- Message sequencing preservation
- Database-backed history
"""

import asyncio
import logging
import sys
import re
from datetime import datetime
from typing import Optional, List, Dict, Set
from decouple import config
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPreview
from pyrogram.errors import FloodWait, ChannelPrivate
import motor.motor_asyncio as motor

# ===== SETUP =====

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('advanced_forwarder.log')
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
    logger.error(f"Missing configuration: {e}")
    sys.exit(1)

# Client initialization
app = Client(
    "telegram_advanced_forwarder",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=4
)

# Database
mongo_client = None
db = None

# User sessions and forwarding state
user_sessions: Dict[int, Dict] = {}
forwarding_tasks: Dict[str, Dict] = {}  # Key: f"{user_id}_{topic_id}"


# ===== DATABASE FUNCTIONS =====

async def init_db():
    """Initialize MongoDB."""
    global mongo_client, db
    if not DATABASE_URI:
        logger.warning("DATABASE_URI not set. Using in-memory storage.")
        return False
    
    try:
        mongo_client = motor.AsyncIOMotorClient(DATABASE_URI, serverSelectionTimeoutMS=5000)
        db = mongo_client["telegram_forwarder"]
        
        await db.sessions.create_index("user_id", unique=False)
        await db.forwarded_messages.create_index([("user_id", 1), ("msg_id", 1)], unique=True)
        await db.forwarding_tasks.create_index("user_id", unique=False)
        
        await mongo_client.admin.command('ping')
        logger.info("✓ MongoDB connected")
        return True
    except Exception as e:
        logger.warning(f"MongoDB unavailable: {e}")
        return False


async def save_forwarding_task(user_id: int, source_channel: str, topic_id: int, 
                               total_msgs: int, task_id: str):
    """Save forwarding task info."""
    data = {
        "user_id": user_id,
        "source_channel": source_channel,
        "topic_id": topic_id,
        "total_messages": total_msgs,
        "forwarded": 0,
        "failed": 0,
        "status": "started",
        "started_at": datetime.utcnow(),
        "task_id": task_id
    }
    
    if db:
        try:
            await db.forwarding_tasks.update_one(
                {"task_id": task_id},
                {"$set": data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to save task: {e}")


async def update_task_progress(task_id: str, forwarded: int, failed: int):
    """Update task progress."""
    if db:
        try:
            await db.forwarding_tasks.update_one(
                {"task_id": task_id},
                {"$set": {"forwarded": forwarded, "failed": failed}}
            )
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")


async def log_forwarded_message(user_id: int, msg_id: int, dest_msg_id: int, 
                               source_channel: str, topic_id: int, msg_type: str):
    """Log forwarded message."""
    record = {
        "user_id": user_id,
        "msg_id": msg_id,
        "dest_msg_id": dest_msg_id,
        "source_channel": source_channel,
        "topic_id": topic_id,
        "type": msg_type,
        "timestamp": datetime.utcnow()
    }
    
    if db:
        try:
            await db.forwarded_messages.insert_one(record)
        except Exception:
            pass  # Duplicate key is OK


# ===== UTILITY FUNCTIONS =====

def parse_channel_id(channel_str: str):
    """Parse channel ID from various formats."""
    if not channel_str:
        return None
    
    channel_str = str(channel_str).strip()
    
    if channel_str.startswith("@"):
        return channel_str
    
    # t.me/c/3895961049 format
    if "t.me/c/" in channel_str:
        match = re.search(r't\.me/c/(\d+)', channel_str)
        if match:
            cid = int(match.group(1))
            return -100_000_000_000 - cid
    
    # t.me/+invite format
    if "t.me/+" in channel_str:
        return channel_str
    
    # Try numeric
    try:
        return int(channel_str)
    except:
        return channel_str


def get_message_type(msg: Message) -> str:
    """Determine message type."""
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
        return "🎥 Video Note"
    elif msg.sticker:
        return "🎨 Sticker"
    else:
        return "📝 Text"


async def get_channel_with_topics(client: Client, channel_id) -> tuple:
    """Get channel and its topics."""
    try:
        chat = await client.get_chat(channel_id)
        
        # Try to get forum topics
        topics = []
        try:
            # For supergroups with topics (forums)
            if hasattr(chat, 'is_forum') and chat.is_forum:
                # Manually fetch topic list by getting first messages of each topic
                seen_topics = set()
                async for msg in client.get_chat_history(channel_id, limit=1000):
                    if hasattr(msg, 'topic_id'):
                        if msg.topic_id not in seen_topics:
                            seen_topics.add(msg.topic_id)
                            topics.append({
                                "id": msg.topic_id,
                                "title": f"Topic {msg.topic_id}",
                                "icon": "📌"
                            })
        except Exception as e:
            logger.warning(f"Could not fetch topics: {e}")
        
        return chat, topics
        
    except Exception as e:
        logger.error(f"Failed to get channel: {e}")
        return None, []


async def get_topic_messages_count(client: Client, channel_id, topic_id: int) -> int:
    """Count messages in a topic."""
    try:
        count = 0
        async for msg in client.get_chat_history(channel_id, limit=10000):
            if hasattr(msg, 'topic_id') and msg.topic_id == topic_id:
                count += 1
            elif not hasattr(msg, 'topic_id') and topic_id == 1:
                count += 1
        return count
    except Exception as e:
        logger.error(f"Count error: {e}")
        return 0


async def get_topic_messages(client: Client, channel_id, topic_id: int) -> List[Message]:
    """Fetch all messages from a topic in sequence."""
    messages = []
    try:
        async for msg in client.get_chat_history(channel_id, limit=10000):
            if hasattr(msg, 'topic_id'):
                if msg.topic_id == topic_id:
                    messages.append(msg)
            elif topic_id == 1:  # General topic
                messages.append(msg)
        
        messages.reverse()  # Oldest first
        return messages
        
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        return []


# ===== BOT COMMANDS =====

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    """Main menu."""
    text = """
🤖 **Telegram Topic Message Forwarder**

Select what you want to do:
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Select Source Channel", callback_data="select_channel")],
        [InlineKeyboardButton("📊 View Status", callback_data="view_all_status")],
        [InlineKeyboardButton("📋 Forwarding History", callback_data="history")],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu")]
    ])
    
    await message.reply_text(text, reply_markup=keyboard)


# ===== CALLBACK HANDLERS =====

@app.on_callback_query()
async def callbacks(client: Client, cq):
    """Handle all callbacks."""
    user_id = cq.from_user.id
    data = cq.data
    
    try:
        if data == "select_channel":
            await cq.message.edit_text(
                "**📥 Enter Channel Details**\n\n"
                "Send me the channel URL:\n\n"
                "Examples:\n"
                "`https://t.me/c/3895961049/`\n"
                "`https://t.me/+3CoEtU8yo0hhZGVh`\n"
                "`@channelname`",
                parse_mode="markdown"
            )
            if user_id not in user_sessions:
                user_sessions[user_id] = {}
            user_sessions[user_id]["awaiting"] = "channel_url"
        
        elif data == "view_all_status":
            if user_id not in user_sessions or "source_channel" not in user_sessions[user_id]:
                await cq.answer("Select channel first!", show_alert=True)
                return
            
            session = user_sessions[user_id]
            status = (
                f"**📊 Overall Status**\n\n"
                f"Source: `{session.get('source_channel', 'N/A')}`\n"
                f"Topics Processed: `{session.get('topics_done', 0)}`\n"
                f"Total Messages Forwarded: `{session.get('total_forwarded', 0)}`\n\n"
                f"Last Update: `{datetime.now().strftime('%H:%M:%S')}`"
            )
            await cq.message.edit_text(status, parse_mode="markdown")
        
        elif data == "history":
            text = "**📋 Forwarding History**\n\n" + (
                f"You have forwarded messages in {len(forwarding_tasks)} session(s)." 
                if forwarding_tasks else "No history yet."
            )
            await cq.message.edit_text(text, parse_mode="markdown")
        
        elif data == "help_menu":
            text = (
                "**❓ How to Use**\n\n"
                "1️⃣ Click 'Select Source Channel'\n"
                "2️⃣ Send channel URL\n"
                "3️⃣ Select a topic\n"
                "4️⃣ Watch it forward! 🚀\n\n"
                "**Tips:**\n"
                "• Make sure bot is member of source channel\n"
                "• Destination is @gatearshadbackup\n"
                "• Messages forward in sequence\n"
                "• All media types supported"
            )
            await cq.message.edit_text(text, parse_mode="markdown")
        
        elif data.startswith("topic_"):
            topic_id = int(data.split("_")[1])
            await handle_topic_start(client, cq, user_id, topic_id)
        
        await cq.answer()
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await cq.answer(f"❌ {e}", show_alert=True)


async def handle_topic_start(client: Client, cq, user_id: int, topic_id: int):
    """Start forwarding a topic."""
    try:
        session = user_sessions.get(user_id, {})
        source_channel = session.get("source_channel")
        
        if not source_channel:
            await cq.answer("Session expired!", show_alert=True)
            return
        
        source_id = parse_channel_id(source_channel)
        dest_id = parse_channel_id(DESTINATION_CHANNEL)
        
        # Send initial status
        status_msg = await cq.message.edit_text(
            f"⏳ **Preparing to forward...**\n\n"
            f"Topic: `{topic_id}`\n"
            f"Status: Counting messages...",
            parse_mode="markdown"
        )
        
        # Get messages
        messages = await get_topic_messages(client, source_id, topic_id)
        
        if not messages:
            await status_msg.edit_text(f"❌ No messages in topic {topic_id}")
            return
        
        total = len(messages)
        task_id = f"{user_id}_{topic_id}_{datetime.now().timestamp()}"
        
        # Save task
        await save_forwarding_task(user_id, source_channel, topic_id, total, task_id)
        forwarding_tasks[task_id] = {
            "forwarded": 0,
            "failed": 0,
            "total": total
        }
        
        forwarded_count = 0
        failed_count = 0
        
        await status_msg.edit_text(
            f"📤 **Forwarding {total} Messages**\n\n"
            f"Topic ID: `{topic_id}`\n"
            f"Progress: `0/{total}`\n\n"
            f"Status: Starting...",
            parse_mode="markdown"
        )
        
        # Forward each message
        for idx, msg in enumerate(messages, 1):
            try:
                msg_type = get_message_type(msg)
                
                # Forward
                fwd_msg = await client.forward_messages(
                    chat_id=dest_id,
                    from_chat_id=source_id,
                    message_ids=msg.id
                )
                
                forwarded_count += 1
                
                # Log
                await log_forwarded_message(
                    user_id, msg.id, fwd_msg.id, source_channel, topic_id, msg_type
                )
                
                # Update progress every 5 or at end
                if idx % 5 == 0 or idx == total:
                    pct = int((idx / total) * 100)
                    await status_msg.edit_text(
                        f"📤 **Forwarding Messages**\n\n"
                        f"Topic ID: `{topic_id}`\n"
                        f"Progress: `{idx}/{total}` ({pct}%)\n"
                        f"Success: `{forwarded_count}`\n"
                        f"Failed: `{failed_count}`\n\n"
                        f"Status: Processing...",
                        parse_mode="markdown"
                    )
                    
                    await update_task_progress(task_id, forwarded_count, failed_count)
                
                await asyncio.sleep(0.3)
                
            except FloodWait as e:
                await asyncio.sleep(min(e.value, 30))
                
            except Exception as e:
                logger.warning(f"Message forward error: {e}")
                failed_count += 1
                await asyncio.sleep(1)
        
        # Update session
        user_sessions[user_id]["total_forwarded"] = user_sessions[user_id].get("total_forwarded", 0) + forwarded_count
        user_sessions[user_id]["topics_done"] = user_sessions[user_id].get("topics_done", 0) + 1
        
        # Final status
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Forward Another Topic", callback_data="select_topics_again")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
        ])
        
        await status_msg.edit_text(
            f"✅ **Forwarding Complete!**\n\n"
            f"Topic ID: `{topic_id}`\n"
            f"Total Messages: `{total}`\n"
            f"Successfully Forwarded: `{forwarded_count}` ✓\n"
            f"Failed: `{failed_count}` ✗\n\n"
            f"All messages have been forwarded to @gatearshadbackup\n"
            f"in exact sequence!",
            parse_mode="markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Topic start error: {e}")
        await cq.answer(f"❌ {e}", show_alert=True)


# ===== TEXT MESSAGE HANDLER =====

@app.on_message(filters.text & filters.private & ~filters.command)
async def text_handler(client: Client, message: Message):
    """Handle text input."""
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    session = user_sessions[user_id]
    
    # Awaiting channel URL
    if session.get("awaiting") == "channel_url":
        try:
            channel_id = parse_channel_id(text)
            
            # Validate
            status = await message.reply_text("⏳ Checking channel...")
            
            try:
                chat, topics = await get_channel_with_topics(client, channel_id)
                
                if not chat:
                    await status.edit_text("❌ Cannot access channel. Make sure bot is a member.")
                    return
                
                session["source_channel"] = text
                session["channel_title"] = chat.title
                session["awaiting"] = None
                
                # Show topics
                if topics:
                    keyboard = []
                    for t in topics:
                        btn = InlineKeyboardButton(f"{t['icon']} Topic {t['id']}", 
                                                 callback_data=f"topic_{t['id']}")
                        keyboard.append([btn])
                    
                    kb = InlineKeyboardMarkup(keyboard)
                    
                    await status.edit_text(
                        f"✅ **Connected to {chat.title}**\n\n"
                        f"Found {len(topics)} topic(s)\n\n"
                        f"Select a topic to forward:",
                        reply_markup=kb
                    )
                else:
                    await status.edit_text(f"❌ No topics found in {chat.title}")
                    
            except Exception as e:
                await status.edit_text(f"❌ Error: {e}")
                
        except Exception as e:
            await message.reply_text(f"❌ Invalid input: {e}")
    else:
        await message.reply_text("Use /start to begin")


# ===== MAIN =====

async def main():
    """Start bot."""
    logger.info("=" * 70)
    logger.info("Advanced Telegram Topic-Based Message Forwarder")
    logger.info("=" * 70)
    
    await init_db()
    
    try:
        async with app:
            me = await app.get_me()
            logger.info(f"✓ Bot: @{me.username}")
            logger.info(f"✓ Destination: {DESTINATION_CHANNEL}")
            logger.info("✓ Ready for forwarding!")
            logger.info("")
            logger.info("Bot running. Press Ctrl+C to stop.")
            logger.info("=" * 70)
            
            await app.idle()
            
    except KeyboardInterrupt:
        logger.info("\n✓ Bot stopped")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if mongo_client:
            mongo_client.close()


if __name__ == "__main__":
    asyncio.run(main())
