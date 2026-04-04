#!/usr/bin/env python3
"""
Telegram Topic-Based Message Forwarder Bot
Features:
- Select source channel with topic support
- Display available topics
- Select specific topic to forward
- Forward all messages (text, media, documents) in sequence
- Real-time status tracking
- Database for tracking forwarded messages
"""

import asyncio
import logging
import sys
import json
from datetime import datetime
from typing import Optional, List, Dict
from decouple import config
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import motor.motor_asyncio as motor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('forwarder_bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Load configuration from environment
try:
    API_ID = int(config("API_ID"))
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    OWNER_ID = int(config("BOT_OWNER_ID", default="0"))
    DATABASE_URI = config("DATABASE", default=None)
    DESTINATION_CHANNEL = config("DESTINATION_CHANNEL")
except Exception as e:
    logger.error(f"Missing configuration: {e}")
    sys.exit(1)

# Initialize Pyrogram client
app = Client(
    "telegram_topic_forwarder",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=4
)

# MongoDB setup
mongo_client = None
db = None

# In-memory storage for user sessions
user_sessions: Dict[int, Dict] = {}


async def init_db():
    """Initialize MongoDB connection."""
    global mongo_client, db
    if not DATABASE_URI:
        logger.warning("DATABASE_URI not set. Using in-memory storage only.")
        return False
    
    try:
        mongo_client = motor.AsyncIOMotorClient(DATABASE_URI)
        db = mongo_client["telegram_forwarder"]
        
        # Create collections with indexes
        await db.forwarding_sessions.create_index("user_id", unique=False)
        await db.forwarded_messages.create_index([("user_id", 1), ("source_msg_id", 1)], unique=True)
        await db.forwarded_messages.create_index("timestamp")
        
        # Test connection
        await mongo_client.admin.command('ping')
        logger.info("✓ MongoDB connected successfully")
        return True
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Using in-memory storage only.")
        return False


async def save_session(user_id: int, source_channel: str, topics: List[Dict]):
    """Save user session to database or memory."""
    session_data = {
        "user_id": user_id,
        "source_channel": source_channel,
        "topics": topics,
        "timestamp": datetime.utcnow()
    }
    
    user_sessions[user_id] = session_data
    
    if db:
        try:
            await db.forwarding_sessions.update_one(
                {"user_id": user_id},
                {"$set": session_data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to save session to DB: {e}")


async def save_forwarded_message(user_id: int, source_msg_id: int, dest_msg_id: int, 
                                  source_channel: str, topic_id: int, message_type: str):
    """Track forwarded message."""
    record = {
        "user_id": user_id,
        "source_msg_id": source_msg_id,
        "dest_msg_id": dest_msg_id,
        "source_channel": source_channel,
        "topic_id": topic_id,
        "message_type": message_type,
        "timestamp": datetime.utcnow()
    }
    
    if db:
        try:
            await db.forwarded_messages.insert_one(record)
        except Exception as e:
            if "duplicate key error" not in str(e):
                logger.error(f"Failed to save forwarded message: {e}")


async def get_forwarding_status(user_id: int, source_channel: str, topic_id: int) -> Dict:
    """Get status of forwarded messages."""
    if not db:
        return {"total": 0, "forwarded": 0, "failed": 0}
    
    try:
        total = await db.forwarded_messages.count_documents({
            "user_id": user_id,
            "source_channel": source_channel,
            "topic_id": topic_id
        })
        
        return {"total": total, "status": "Forwarding status available"}
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return {"error": str(e)}


def parse_channel_id(channel_str: str):
    """Parse channel ID from URL, username, or numeric ID."""
    if not channel_str:
        return None
    
    channel_str = str(channel_str).strip()
    
    # Handle @username format
    if channel_str.startswith("@"):
        return channel_str
    
    # Handle t.me/c/123456789 (private channel)
    if "t.me/c/" in channel_str:
        import re
        match = re.search(r't\.me/c/(\d+)', channel_str)
        if match:
            channel_id = int(match.group(1))
            formatted_id = -100_000_000_000 - channel_id
            return formatted_id
    
    # Handle t.me/+invite (private channel invite)
    if "t.me/+" in channel_str:
        return channel_str
    
    # Handle numeric ID
    try:
        return int(channel_str)
    except ValueError:
        return channel_str


async def get_channel_topics(client: Client, channel_id) -> List[Dict]:
    """Get all topics from a channel."""
    try:
        # Get channel info
        chat = await client.get_chat(channel_id)
        
        if not hasattr(chat, 'topics') or not chat.topics:
            logger.warning(f"Channel {channel_id} has no topics or topics not accessible")
            return []
        
        topics = []
        for topic in chat.topics:
            topics.append({
                "id": topic.id,
                "title": topic.title,
                "icon_emoji": getattr(topic, 'icon_emoji', '📌'),
                "icon_custom_emoji_id": getattr(topic, 'icon_custom_emoji_id', None)
            })
        
        logger.info(f"Found {len(topics)} topics in channel {channel_id}")
        return topics
        
    except Exception as e:
        logger.error(f"Failed to get topics: {e}")
        return []


async def get_topic_messages(client: Client, channel_id, topic_id: int = 1, limit: int = None) -> List[Message]:
    """Get all messages from a specific topic."""
    messages = []
    try:
        # Get messages from topic
        async for msg in client.get_chat_history(channel_id, offset_id=0):
            # Filter messages by topic
            if hasattr(msg, 'topic_id') and msg.topic_id == topic_id:
                messages.append(msg)
            elif not hasattr(msg, 'topic_id') and topic_id == 1:
                # General topic
                messages.append(msg)
            
            if limit and len(messages) >= limit:
                break
        
        # Reverse to maintain original sequence (oldest first)
        messages.reverse()
        logger.info(f"Found {len(messages)} messages in topic {topic_id}")
        return messages
        
    except Exception as e:
        logger.error(f"Failed to get topic messages: {e}")
        return []


# ===== BOT COMMAND HANDLERS =====

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Start command - show main menu."""
    text = """
👋 **Welcome to Telegram Topic Forwarder Bot!**

This bot helps you forward messages from a specific channel topic to your destination channel.

**Features:**
✅ Select source channel
✅ View all topics
✅ Forward messages topic-by-topic
✅ Track forwarding status
✅ Support for all media types (video, pdf, text, etc.)

**How to use:**
1. Tap **Select Source Channel** button below
2. Enter the channel URL or invite link
3. View available topics
4. Select a topic to start forwarding
5. Monitor the status

Let's get started! 👇
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Select Source Channel", callback_data="select_channel")],
        [InlineKeyboardButton("📊 View Status", callback_data="view_status")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ])
    
    await message.reply_text(text, reply_markup=keyboard)


@app.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Help command."""
    text = """
**How to Use This Bot:**

1. **Select Source Channel:**
   - Click "Select Source Channel" button
   - Paste channel URL (e.g., https://t.me/c/3895961049/)
   - Or invite link (e.g., https://t.me/+3CoEtU8yo0hhZGVh)

2. **View Topics:**
   - After selecting channel, available topics will be shown
   - Each topic is listed with its icon and title

3. **Forward Messages:**
   - Select a topic from the list
   - Bot will forward ALL messages in sequence
   - Media, documents, and text will be preserved
   - Forwarding continues in exact order

4. **Monitor Status:**
   - Use "View Status" button to check progress
   - See number of messages forwarded
   - Real-time updates as forwarding progresses

**Important Notes:**
- Bot must be member of source channel
- Destination channel is: @gatearshadbackup
- Messages are forwarded maintaining original sequence
- Status updates every few seconds

**Need Help?**
Contact the bot owner for support.
"""
    await message.reply_text(text)


@app.on_callback_query()
async def callback_handler(client: Client, callback_query):
    """Handle all callback queries."""
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    try:
        if data == "select_channel":
            await callback_query.message.edit_text(
                "📥 **Enter Source Channel**\n\n"
                "Send me the channel URL or invite link:\n\n"
                "Examples:\n"
                "• `https://t.me/c/3895961049/` (public channel)\n"
                "• `https://t.me/+3CoEtU8yo0hhZGVh` (private/invite link)\n"
                "• `@channel_username` (public channel username)",
                parse_mode="markdown"
            )
            user_sessions[user_id] = {"waiting_for": "channel"}
        
        elif data == "view_status":
            if user_id not in user_sessions or "source_channel" not in user_sessions[user_id]:
                await callback_query.answer("❌ Please select a channel first!", show_alert=True)
                return
            
            session = user_sessions[user_id]
            status_text = f"""
📊 **Forwarding Status**

Source Channel: `{session['source_channel']}`
Selected Topic: `{session.get('selected_topic', 'None')}`

Total Messages Forwarded: `{session.get('total_forwarded', 0)}`
Failed: `{session.get('failed_count', 0)}`
Pending: `{session.get('pending_count', 0)}`

Status: `{session.get('status', 'Idle')}`
Last Update: `{session.get('last_update', 'Never')}`
"""
            await callback_query.message.edit_text(status_text, parse_mode="markdown")
        
        elif data == "help":
            await callback_query.message.edit_text(
                "**How to Use This Bot:**\n\n"
                "1. Select source channel with topic\n"
                "2. View available topics\n"
                "3. Forward messages from topic\n"
                "4. Monitor real-time status\n\n"
                "Use /help for detailed instructions."
            )
        
        elif data.startswith("topic_"):
            topic_id = int(data.split("_")[1])
            await handle_topic_selection(client, callback_query, user_id, topic_id)
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)


async def handle_topic_selection(client: Client, callback_query, user_id: int, topic_id: int):
    """Handle topic selection and start forwarding."""
    try:
        if user_id not in user_sessions or "source_channel" not in user_sessions[user_id]:
            await callback_query.answer("❌ Session expired. Please select channel again.", show_alert=True)
            return
        
        session = user_sessions[user_id]
        source_channel = session["source_channel"]
        source_id = parse_channel_id(source_channel)
        dest_id = parse_channel_id(DESTINATION_CHANNEL)
        
        status_msg = await callback_query.message.edit_text(
            f"⏳ **Starting forwarding...**\n\n"
            f"Source: `{source_channel}`\n"
            f"Topic: `{topic_id}`\n"
            f"Destination: `{DESTINATION_CHANNEL}`\n\n"
            f"Status: Retrieving messages...",
            parse_mode="markdown"
        )
        
        # Get messages from topic
        messages = await get_topic_messages(client, source_id, topic_id)
        
        if not messages:
            await status_msg.edit_text(f"❌ No messages found in topic {topic_id}")
            return
        
        session["total_messages"] = len(messages)
        session["forwarded_count"] = 0
        session["failed_count"] = 0
        session["selected_topic"] = topic_id
        session["status"] = "Forwarding"
        
        await status_msg.edit_text(
            f"📤 **Forwarding Messages**\n\n"
            f"Topic: `{topic_id}`\n"
            f"Total Messages: `{len(messages)}`\n\n"
            f"Progress: `0/{len(messages)}`\n"
            f"Status: Starting...",
            parse_mode="markdown"
        )
        
        # Forward messages one by one
        for idx, msg in enumerate(messages, 1):
            try:
                # Determine message type
                msg_type = "text"
                if msg.media:
                    if msg.video:
                        msg_type = "video"
                    elif msg.document:
                        msg_type = "document"
                    elif msg.photo:
                        msg_type = "photo"
                    elif msg.audio:
                        msg_type = "audio"
                    elif msg.voice:
                        msg_type = "voice"
                
                # Forward message
                forwarded = await client.forward_messages(
                    chat_id=dest_id,
                    from_chat_id=source_id,
                    message_ids=msg.id
                )
                
                session["forwarded_count"] += 1
                
                # Save to database
                await save_forwarded_message(
                    user_id, msg.id, forwarded.id, source_channel, topic_id, msg_type
                )
                
                # Update status every 5 messages or on last message
                if idx % 5 == 0 or idx == len(messages):
                    percentage = int((idx / len(messages)) * 100)
                    await status_msg.edit_text(
                        f"📤 **Forwarding Messages**\n\n"
                        f"Topic: `{topic_id}`\n"
                        f"Total: `{len(messages)}`\n\n"
                        f"Progress: `{idx}/{len(messages)}` ({percentage}%)\n"
                        f"Status: Forwarding... ✓",
                        parse_mode="markdown"
                    )
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except FloodWait as e:
                logger.warning(f"Flood wait: {e.value}s")
                await asyncio.sleep(min(e.value, 60))
                
            except Exception as e:
                logger.error(f"Failed to forward message {msg.id}: {e}")
                session["failed_count"] += 1
                await asyncio.sleep(1)
        
        session["status"] = "Completed"
        session["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Final status
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Select Another Topic", callback_data="select_topics")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
        ])
        
        await status_msg.edit_text(
            f"✅ **Forwarding Complete!**\n\n"
            f"Topic: `{topic_id}`\n"
            f"Total Messages: `{len(messages)}`\n"
            f"Successfully Forwarded: `{session['forwarded_count']}`\n"
            f"Failed: `{session['failed_count']}`\n\n"
            f"All messages have been forwarded to @gatearshadbackup in sequence!",
            parse_mode="markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Topic selection error: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)


@app.on_message(filters.text & filters.private)
async def text_message_handler(client: Client, message: Message):
    """Handle text messages (channel URLs, etc.)."""
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    session = user_sessions[user_id]
    
    if session.get("waiting_for") == "channel":
        try:
            # Validate channel URL/username
            if not (text.startswith("http") or text.startswith("@") or text.isdigit()):
                await message.reply_text("❌ Invalid format. Please send a valid channel URL or @username")
                return
            
            channel_id = parse_channel_id(text)
            
            # Try to get channel info
            try:
                chat = await client.get_chat(channel_id)
                logger.info(f"✓ Got channel: {chat.title}")
            except Exception as e:
                await message.reply_text(f"❌ Cannot access channel: {e}\n\nMake sure the bot is a member of the channel.")
                return
            
            session["source_channel"] = text
            session["waiting_for"] = None
            
            # Get topics
            topics = await get_channel_topics(client, channel_id)
            
            if not topics:
                await message.reply_text(
                    f"❌ No topics found in this channel.\n\n"
                    f"Channel: `{text}`\n\n"
                    f"This channel either:\n"
                    f"• Doesn't have topics enabled\n"
                    f"• Topics are not accessible\n\n"
                    f"Try another channel.",
                    parse_mode="markdown"
                )
                return
            
            session["topics"] = topics
            
            # Show topics
            keyboard_buttons = []
            for topic in topics:
                btn_text = f"{topic['icon_emoji']} {topic['title']}"
                keyboard_buttons.append([
                    InlineKeyboardButton(btn_text, callback_data=f"topic_{topic['id']}")
                ])
            
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            await message.reply_text(
                f"✅ **Channel Connected!**\n\n"
                f"Channel: `{text}`\n"
                f"Topics Found: `{len(topics)}`\n\n"
                f"Select a topic to forward all its messages:",
                parse_mode="markdown",
                reply_markup=keyboard
            )
            
            # Save session
            await save_session(user_id, text, topics)
            
        except Exception as e:
            logger.error(f"Channel handling error: {e}")
            await message.reply_text(f"❌ Error: {e}")
    else:
        await message.reply_text(
            "👋 Use /start to begin or select an option from the menu."
        )


async def main():
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("Telegram Topic-Based Message Forwarder Bot")
    logger.info("=" * 70)
    
    # Initialize database
    await init_db()
    
    try:
        async with app:
            me = await app.get_me()
            logger.info(f"✓ Connected as: @{me.username} (ID: {me.id})")
            logger.info(f"✓ Bot is ready to forward messages")
            logger.info(f"✓ Destination Channel: {DESTINATION_CHANNEL}")
            logger.info("")
            logger.info("Bot is running. Press Ctrl+C to stop.")
            logger.info("=" * 70)
            
            await app.idle()
            
    except KeyboardInterrupt:
        logger.info("\n✓ Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if mongo_client:
            mongo_client.close()


if __name__ == "__main__":
    asyncio.run(main())
