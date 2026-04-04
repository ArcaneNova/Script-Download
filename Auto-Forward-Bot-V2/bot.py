import asyncio
import logging 
import logging.config
import re
from database import db 
from config import Config  
from pyrogram import Client, __version__, filters
from pyrogram.raw.all import layer 
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait 

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client): 
    def __init__(self):
        # Only load plugins if NOT in auto-forward mode
        plugins_config = {}
        if not (Config.SOURCE_CHANNEL and Config.DESTINATION_CHANNEL):
            plugins_config = {"root": "plugins"}
        
        super().__init__(
            Config.BOT_SESSION,
            api_hash=Config.API_HASH,
            api_id=Config.API_ID,
            plugins=plugins_config,
            workers=50,
            bot_token=Config.BOT_TOKEN
        )
        self.log = logging

    async def start(self):
        # Retry logic to handle Telegram handshake failures
        max_retries = 5
        for attempt in range(max_retries):
            try:
                logging.info(f"Connecting to Telegram (attempt {attempt + 1}/{max_retries})...")
                await asyncio.wait_for(super().start(), timeout=30)
                break
            except asyncio.TimeoutError:
                logging.warning(f"Connection timeout, retrying... ({attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logging.error("Failed to connect after maximum retries")
                    raise
            except (KeyError, Exception) as e:
                logging.warning(f"Connection error: {e}, retrying... ({attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logging.error(f"Failed to connect: {e}")
                    raise
        
        me = await self.get_me()
        logging.info(f"{me.first_name} with for pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
        self.id = me.id
        self.username = me.username
        self.first_name = me.first_name
        self.set_parse_mode(ParseMode.DEFAULT)
        text = "**๏[-ิ_•ิ]๏ bot restarted !**"
        logging.info(text)
        
        # Start auto-forward listener if channels are configured
        if Config.SOURCE_CHANNEL and Config.DESTINATION_CHANNEL:
            logging.info(f"Starting auto-forward from {Config.SOURCE_CHANNEL} to {Config.DESTINATION_CHANNEL}")
            asyncio.create_task(self.auto_forward_messages())

        # Check if database URI is default broken one
        if "mongodb+srv://chhjgjkkjhkjhkjh@cluster0.xowzpr4.mongodb.net/" in Config.DATABASE_URI:
             logging.error("You have not set the DATABASE environment variable. The bot will not function correctly.")
             return

        try:
            success = failed = 0
            users = await db.get_all_frwd()
            async for user in users:
               chat_id = user['user_id']
               try:
                  await self.send_message(chat_id, text)
                  success += 1
               except FloodWait as e:
                  await asyncio.sleep(e.value + 1)
                  await self.send_message(chat_id, text)
                  success += 1
               except Exception:
                  failed += 1

            if (success + failed) != 0:
               await db.rmve_frwd(all=True)
               logging.info(f"Restart message status"
                     f"success: {success}"
                     f"failed: {failed}")
        except Exception as e:
            logging.error(f"Failed to send restart messages or connect to DB: {e}")

    async def auto_forward_messages(self):
        """Auto-forward messages from SOURCE_CHANNEL to DESTINATION_CHANNEL."""
        try:
            src_id = self._parse_channel_id(Config.SOURCE_CHANNEL)
            dest_id = self._parse_channel_id(Config.DESTINATION_CHANNEL)
            
            logging.info(f"Auto-forward: Listening on {src_id}, forwarding to {dest_id}")
            
            @self.on_message(filters.chat(src_id))
            async def forward_handler(client, message):
                try:
                    if message.service:
                        return
                    
                    await client.forward_messages(
                        chat_id=dest_id,
                        from_chat_id=src_id,
                        message_ids=message.id
                    )
                    logging.info(f"Forwarded message {message.id}")
                except FloodWait as e:
                    await asyncio.sleep(e.value + 1)
                    await client.forward_messages(
                        chat_id=dest_id,
                        from_chat_id=src_id,
                        message_ids=message.id
                    )
                except Exception as e:
                    logging.error(f"Failed to forward message {message.id}: {e}")
        except Exception as e:
            logging.error(f"Auto-forward error: {e}")
    
    def _parse_channel_id(self, channel_str):
        """Parse channel ID from URL, username, or direct ID."""
        if not channel_str:
            return None
        
        # Handle private channel URLs like https://t.me/+3CoEtU8yo0hhZGVh
        if "t.me/" in channel_str:
            import re
            # Try to extract numeric ID or username
            match = re.search(r't\.me/c/(\d+)', channel_str)
            if match:
                # This is a private channel ID
                channel_id = int(match.group(1))
                return -100 * 1000000000 - channel_id  # Convert to Pyrogram format
            
            match = re.search(r't\.me/\+?([a-zA-Z0-9_-]+)', channel_str)
            if match:
                username_or_id = match.group(1)
                # If numeric, could be a channel ID
                if username_or_id.isdigit():
                    return int(username_or_id)
                else:
                    return f"@{username_or_id}"
        
        # Handle @username format
        if channel_str.startswith("@"):
            return channel_str
        
        # Try to parse as integer ID
        try:
            channel_id = int(channel_str)
            # If it's a large number, assume it's a private channel ID
            if channel_id > 1000000000:
                return channel_id
            return channel_id
        except ValueError:
            return channel_str

    async def stop(self, *args):
        msg = f"@{self.username} stopped. Bye."
        await super().stop()
        logging.info(msg)
