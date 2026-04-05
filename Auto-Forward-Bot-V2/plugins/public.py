import re
import asyncio 
from .utils import STS
from database import db
from config import temp 
from translation import Translation
from .link_parser import parse_telegram_link
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait 
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate as PrivateChat
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified, ChannelPrivate
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
 
#===================Run Function===================#

@Client.on_message(filters.private & filters.command(["fwd", "forward"]))
async def run(bot, message):
    buttons = []
    btn_data = {}
    user_id = message.from_user.id
    _bot = await db.get_bot(user_id)
    if not _bot:
      return await message.reply("<code>You didn't added any bot. Please add a bot using /settings !</code>")
    channels = await db.get_user_channels(user_id)
    if not channels:
       return await message.reply_text("please set a to channel in /settings before forwarding")
    if len(channels) > 1:
       for channel in channels:
          buttons.append([KeyboardButton(f"{channel['title']}")])
          btn_data[channel['title']] = channel['chat_id']
       buttons.append([KeyboardButton("cancel")]) 
       _toid = await bot.ask(message.chat.id, Translation.TO_MSG.format(_bot['name'], _bot['username']), reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
       if _toid.text.startswith(('/', 'cancel')):
          return await message.reply_text(Translation.CANCEL, reply_markup=ReplyKeyboardRemove())
       to_title = _toid.text
       toid = btn_data.get(to_title)
       if not toid:
          return await message.reply_text("wrong channel choosen !", reply_markup=ReplyKeyboardRemove())
    else:
       toid = channels[0]['chat_id']
       to_title = channels[0]['title']
    
    fromid = await bot.ask(message.chat.id, Translation.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'):
        await message.reply(Translation.CANCEL)
        return 

    continuous = False
    chat_id = None
    last_msg_id = None
    title = None
    
    # Try to parse as message link first
    if fromid.text and not fromid.forward_date:
        parsed = parse_telegram_link(fromid.text)
        if parsed:
            chat_id, last_msg_id = parsed
            title = "Link Source"
            try:
                title = (await bot.get_chat(chat_id)).title
            except:
                pass
        elif fromid.text.lower() not in ["me", "saved"]:
            return await message.reply('**Invalid message link. Use format: t.me/channel/123 or t.me/c/ID/123 or type "me" for saved messages**')
    
    # Handle "Saved Messages" input
    if fromid.text and fromid.text.lower() in ["me", "saved"]:
        if _bot.get('is_bot'):
            return await message.reply("<b>You cannot forward from Saved Messages using a Bot. Please add a Userbot session via /settings to use this feature.</b>")

        chat_id = "me"
        title = "Saved Messages"

        # Ask for mode: Batch vs Live
        mode_msg = await bot.ask(message.chat.id, Translation.SAVED_MSG_MODE)
        if mode_msg.text.startswith('/'):
             await message.reply(Translation.CANCEL)
             return

        if "live" in mode_msg.text.lower() or "2" in mode_msg.text:
            continuous = True
            last_msg_id = 1000000
        else:
            limit_msg = await bot.ask(message.chat.id, Translation.SAVED_MSG_LIMIT)
            if limit_msg.text.startswith('/'):
                 await message.reply(Translation.CANCEL)
                 return

            if limit_msg.text.lower() == "all":
                 last_msg_id = 10000000
            elif not limit_msg.text.isdigit():
                 await message.reply("Invalid number.")
                 return
            else:
                 last_msg_id = int(limit_msg.text)

    # Handle forwarded message from channel
    elif fromid.forward_from_chat and fromid.forward_from_chat.type in [enums.ChatType.CHANNEL]:
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.username or fromid.forward_from_chat.id
        if last_msg_id == None:
           return await message.reply_text("**This may be a forwarded message from a group and sent by anonymous admin. Please send last message link from group instead**")
        try:
            title = fromid.forward_from_chat.title
        except:
            title = "Forwarded Channel"
    
    # If no valid input was parsed
    if chat_id is None:
        await message.reply_text("**Invalid input! Please either:**\n- **Paste a message link** (t.me/channel/123)\n- **Type** 'me' or 'saved'\n- **Forward a message** from the source")
        return

    if chat_id != "me":
        try:
            if not title:
                title = (await bot.get_chat(chat_id)).title
        except (PrivateChat, ChannelPrivate, ChannelInvalid):
            title = title or "private"
        except (UsernameInvalid, UsernameNotModified):
            return await message.reply('Invalid channel specified.')
        except Exception as e:
            return await message.reply(f'Error: {e}')

    skipno = await bot.ask(message.chat.id, Translation.SKIP_MSG)
    if skipno.text.startswith('/'):
        await message.reply(Translation.CANCEL)
        return
    
    forward_id = f"{user_id}-{skipno.id}"
    buttons = [[
        InlineKeyboardButton('Yes', callback_data=f"start_public_{forward_id}"),
        InlineKeyboardButton('No', callback_data="close_btn")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=Translation.DOUBLE_CHECK.format(botname=_bot['name'], botuname=_bot['username'], from_chat=title, to_chat=to_title, skip=skipno.text),
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    STS(forward_id).store(chat_id, toid, int(skipno.text), int(last_msg_id), continuous=continuous)
