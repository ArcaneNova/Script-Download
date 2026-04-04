#!/usr/bin/env python3
"""
Telegram Topic Message Forwarder Bot
Fresh implementation with simple, reliable handlers
"""

import asyncio
import logging
import sys
import re
from datetime import datetime
from typing import List, Dict
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
forwarding = {}


# ===== DATABASE =====

async def init_db():
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
        logger.warning(f"MongoDB failed: {e}")
        return False


# ===== UTILS =====

def parse_channel(ch_str: str):
    """Parse channel URL/username."""
    if not ch_str:
        return None
    
    ch_str = str(ch_str).strip()
    
    if ch_str.startswith("@"):
        return ch_str
    
    if "t.me/c/" in ch_str:
        m = re.search(r't\.me/c/(\d+)', ch_str)
        if m:
            cid = int(m.group(1))
            return -100_000_000_000 - cid
    
    if "t.me/+" in ch_str:
        return ch_str
    
    try:
        return int(ch_str)
    except:
        return ch_str


def msg_type(msg: Message) -> str:
    """Get message type."""
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
    else:
        return "📝 Text"


async def get_topics(client: Client, ch_id) -> list:
    """Get channel topics."""
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
        logger.error(f"get_topics error: {e}")
        return None, []


async def get_msgs(client: Client, ch_id, topic_id: int) -> list:
    """Get all messages from topic."""
    msgs = []
    try:
        async for msg in client.get_chat_history(ch_id, limit=10000):
            if hasattr(msg, 'topic_id'):
                if msg.topic_id == topic_id:
                    msgs.append(msg)
            elif topic_id == 1:
                msgs.append(msg)
        
        msgs.reverse()
        return msgs
    except Exception as e:
        logger.error(f"get_msgs error: {e}")
        return []


# ===== HANDLERS =====

@app.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    """Start command."""
    logger.info(f"START from {message.from_user.id}")
    
    text = "🤖 **Telegram Topic Forwarder**\n\nWhat do you want?"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Select Channel", callback_data="sel_ch")],
        [InlineKeyboardButton("📊 Status", callback_data="stat")],
        [InlineKeyboardButton("❓ Help", callback_data="hlp")]
    ])
    
    await message.reply_text(text, reply_markup=kb)


@app.on_callback_query()
async def cb(client: Client, cq):
    """Callback handler."""
    uid = cq.from_user.id
    data = cq.data
    
    logger.info(f"Callback: {data} from {uid}")
    
    try:
        if data == "sel_ch":
            await cq.message.edit_text(
                "📥 **Send channel URL:**\n\n"
                "Examples:\n"
                "`https://t.me/c/3895961049/`\n"
                "`https://t.me/+3CoEtU8yo0hhZGVh`\n"
                "`@channelname`",
                parse_mode="markdown"
            )
            sessions[uid] = {"state": "waiting_channel"}
        
        elif data == "stat":
            sess = sessions.get(uid, {})
            text = f"**Status**\n\nChannel: `{sess.get('channel', 'None')}`\nMessages: `{sess.get('total', 0)}`"
            await cq.message.edit_text(text, parse_mode="markdown")
        
        elif data == "hlp":
            await cq.message.edit_text(
                "1️⃣ Click Select Channel\n"
                "2️⃣ Send channel URL\n"
                "3️⃣ Select topic\n"
                "4️⃣ Watch messages forward!"
            )
        
        elif data.startswith("topic_"):
            topic_id = int(data.split("_")[1])
            await forward_topic(client, cq, uid, topic_id)
        
        await cq.answer()
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await cq.answer(f"Error: {e}", show_alert=True)


@app.on_message(filters.text & filters.private & filters.incoming)
async def text(client: Client, message: Message):
    """Text handler."""
    uid = message.from_user.id
    text = message.text.strip()
    
    # Ignore commands
    if text.startswith("/"):
        return
    
    logger.info(f"Text from {uid}: {text[:50]}")
    
    sess = sessions.get(uid, {})
    
    if sess.get("state") == "waiting_channel":
        try:
            # Parse channel
            ch_id = parse_channel(text)
            
            # Validate
            status = await message.reply_text("⏳ Checking...")
            
            try:
                chat, topics = await get_topics(client, ch_id)
                
                if not chat:
                    await status.edit_text("❌ Cannot access. Make sure bot is member.")
                    return
                
                sessions[uid] = {
                    "state": "idle",
                    "channel": text,
                    "channel_id": ch_id,
                    "title": chat.title
                }
                
                if topics:
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📌 {t['title']}", callback_data=f"topic_{t['id']}")]
                        for t in topics
                    ])
                    
                    await status.edit_text(
                        f"✅ **{chat.title}**\n\nTopics: {len(topics)}\n\nSelect topic:",
                        reply_markup=kb
                    )
                else:
                    await status.edit_text(f"❌ No topics in {chat.title}")
                    
            except Exception as e:
                await status.edit_text(f"❌ Error: {e}")
        except Exception as e:
            await message.reply_text(f"❌ Invalid: {e}")
    else:
        await message.reply_text("Use /start first")


async def forward_topic(client: Client, cq, uid: int, topic_id: int):
    """Forward all messages from topic."""
    try:
        sess = sessions.get(uid, {})
        ch_str = sess.get("channel")
        ch_id = sess.get("channel_id")
        
        if not ch_str:
            await cq.answer("No channel selected!", show_alert=True)
            return
        
        dest_id = parse_channel(DESTINATION_CHANNEL)
        
        # Get messages
        status = await cq.message.edit_text(
            f"⏳ Getting messages from topic {topic_id}..."
        )
        
        msgs = await get_msgs(client, ch_id, topic_id)
        
        if not msgs:
            await status.edit_text(f"❌ No messages in topic {topic_id}")
            return
        
        total = len(msgs)
        fwd_count = 0
        fail_count = 0
        
        await status.edit_text(
            f"📤 Forwarding {total} messages...\n\n"
            f"Progress: 0/{total}"
        )
        
        # Forward each
        for idx, msg in enumerate(msgs, 1):
            try:
                await client.forward_messages(
                    chat_id=dest_id,
                    from_chat_id=ch_id,
                    message_ids=msg.id
                )
                fwd_count += 1
                
                # Update every 5
                if idx % 5 == 0 or idx == total:
                    pct = int((idx / total) * 100)
                    await status.edit_text(
                        f"📤 Forwarding...\n\n"
                        f"Progress: {idx}/{total} ({pct}%)\n"
                        f"Success: {fwd_count}\n"
                        f"Failed: {fail_count}"
                    )
                
                await asyncio.sleep(0.3)
                
            except FloodWait as e:
                await asyncio.sleep(min(e.value, 30))
            except Exception as e:
                logger.warning(f"Forward error: {e}")
                fail_count += 1
                await asyncio.sleep(1)
        
        # Final
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Another", callback_data="sel_ch")],
            [InlineKeyboardButton("🏠 Menu", callback_data="menu")]
        ])
        
        await status.edit_text(
            f"✅ Done!\n\n"
            f"Topic: {topic_id}\n"
            f"Total: {total}\n"
            f"Success: {fwd_count} ✓\n"
            f"Failed: {fail_count} ✗\n\n"
            f"Forwarded to @gatearshadbackup",
            reply_markup=kb
        )
        
    except Exception as e:
        logger.error(f"forward_topic error: {e}")
        await cq.answer(f"Error: {e}", show_alert=True)


# ===== MAIN =====

async def main():
    logger.info("=" * 60)
    logger.info("Telegram Topic Forwarder Bot")
    logger.info("=" * 60)
    
    await init_db()
    
    try:
        async with app:
            me = await app.get_me()
            logger.info(f"✓ Bot: @{me.username}")
            logger.info(f"✓ Ready!")
            
            await app.idle()
    except KeyboardInterrupt:
        logger.info("✓ Stopped")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
