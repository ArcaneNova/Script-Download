#!/usr/bin/env python3
"""
Quick Setup Guide for Telegram Topic Forwarder Bot

This guide walks you through:
1. Getting API credentials
2. Creating a bot token
3. Running locally or on Render
4. Using the bot
"""

# ===== QUICK START (5 MINUTES) =====

"""
STEP 1: Get Telegram API Credentials
====================================

1. Go to: https://my.telegram.org/auth?to=apps
2. Log in with your Telegram account
3. Fill in app details (any name works):
   - App title: "Telegram Forwarder"
   - Short name: "forwarder"
   - Platform: "Desktop"

4. Copy the following:
   - API_ID (looks like: 35188145)
   - API_HASH (looks like: 3f725a3cf7a87167a58c4e098c9a1828)


STEP 2: Create Bot with BotFather
==================================

1. Open Telegram
2. Search for: @BotFather
3. Send: /newbot
4. Follow prompts:
   - What should your bot be called? → My Telegram Forwarder
   - Give your bot a username (must end in 'bot'): → my_forwarder_bot

5. Copy the BOT_TOKEN provided
   (looks like: 8695455961:AAFzQOswXeDgkKMbImwI8jDrTd_glAmn39k)


STEP 3: Run Locally (Windows)
==============================

1. Open PowerShell in this folder

2. Create .env file:
   @"
   API_ID=35188145
   API_HASH=3f725a3cf7a87167a58c4e098c9a1828
   BOT_TOKEN=8695455961:AAFzQOswXeDgkKMbImwI8jDrTd_glAmn39k
   DESTINATION_CHANNEL=@your_channel_name
   "@ | Out-File .env

3. Install Python packages:
   pip install -r requirements.txt

4. Run the bot:
   python forwarder_advanced.py

5. In Telegram, find your bot and click /start


STEP 4: Deploy on Render (Free)
================================

1. Fork this repository to GitHub
2. Go to: https://render.com
3. Sign up with GitHub
4. Click "New +" → "Web Service"
5. Select your forked repository
6. Settings:
   - Name: telegram-forwarder
   - Env: Python 3.11
   - Build: pip install -r requirements.txt
   - Start: python forwarder_advanced.py
   - Plan: Free

7. Add Environment Variables:
   - API_ID: 35188145
   - API_HASH: 3f725a3cf7a87167a58c4e098c9a1828
   - BOT_TOKEN: your_bot_token
   - DESTINATION_CHANNEL: @your_channel
   - BOT_OWNER_ID: your_telegram_id

8. Click Deploy
9. Wait 2-3 minutes
10. Bot will be running!


STEP 5: Using the Bot
=====================

1. Open Telegram
2. Find your bot (@my_forwarder_bot)
3. Send: /start
4. Click "📥 Select Source Channel"
5. Send channel URL:
   - For invite links: https://t.me/+3CoEtU8yo0hhZGVh
   - For channels: https://t.me/c/3895961049/
   - For usernames: @channelname

6. Bot shows available topics
7. Click a topic to forward all its messages
8. Watch real-time progress!


TROUBLESHOOTING
===============

❌ "Bot can't access channel"
→ Make sure the bot is a MEMBER of the channel
  - For private channels: Add bot manually
  - For public channels: Join first

❌ "No topics found"
→ Channel must have TOPICS enabled (Forums feature)
  - Check channel has #general and other topics

❌ "Messages not forwarding"
→ Check:
  - Bot has permission to send in destination
  - Destination channel exists
  - API credentials are correct

❌ "AttributeError: 'NoneType' object"
→ Missing .env file or incomplete credentials
  - Create .env with all required variables


IMPORTANT NOTES
===============

✅ Bot must be a MEMBER of:
   - Source channel (where messages come from)
   - Destination channel (where messages go)

✅ Channel URL formats:
   - t.me/c/3895961049/     ← Channel ID number
   - t.me/+3CoEtU8yo0hhZGVh ← Private invite link
   - @channelname           ← Public channel username

✅ The /forward/ part in URLs:
   - https://t.me/c/3895961049/4129/9675
   - /4129/ = Topic ID (shows all topics available)
   - /9675 = Message ID (can forward individual messages)

✅ Finding Your Channel:
   - Right-click channel → Copy link
   - Private channel invite: @BotFather → /newbot instructions
   - For group: Click group info → Copy link


WHAT HAPPENS AFTER DEPLOYMENT
==============================

1. Bot connects to Telegram
2. Waits for you to select a channel
3. You choose source channel
4. You pick a topic
5. Bot forwards ALL messages from that topic in sequence
6. Progress updates in real-time
7. When done, you can select another topic
8. All forwarding logs saved to: forwarder_bot.log


NEXT STEPS
==========

1. ✅ Get API credentials (Step 1)
2. ✅ Create bot token (Step 2)
3. ✅ Choose to run locally (Step 3) or on Render (Step 4)
4. ✅ Use the bot (Step 5)


TIPS FOR SUCCESS
================

📌 Small Test First
   - Try with a channel that has 50-100 messages
   - Make sure forwarding works before large batches

📌 Monitor Logs
   - Locally: Watch terminal output
   - Render: Check dashboard logs for errors

📌 Multiple Topics
   - Can forward different topics to same destination
   - They'll all appear in destination channel

📌 Keep It Running
   - On Render: Runs 24/7 (free tier has limits)
   - Locally: Keep terminal open while using

📌 Message Order
   - Messages forwarded oldest-first (exact sequence)
   - Timestamps preserved
   - All media preserved


COMMON QUESTIONS
================

Q: Can I forward from multiple channels?
A: Yes! Run the bot, select different channels each time

Q: What happens to media files?
A: All preserved - videos, photos, documents, all supported

Q: How fast does it forward?
A: ~200-300 messages/minute (Telegram's rate limit)

Q: Do I need MongoDB?
A: No! Optional. Without it, status tracking works from memory

Q: Can I stop mid-forwarding?
A: Yes, but next time you'll have to restart from beginning
  (unless using database to track)

Q: Is my data safe?
A: Yes! Only forwarded messages stored, bot token in env vars

Q: Can I use on mobile?
A: No, bot runs on server. Control it via Telegram chat


API CREDENTIAL SAFETY
=====================

🔒 NEVER share:
   - API_HASH
   - BOT_TOKEN
   - DATABASE URL

🔒 ALWAYS:
   - Keep .env file private (add to .gitignore)
   - Use environment variables
   - Regenerate tokens if compromised

🔒 In Render/Server:
   - Use "Reveal" button only when needed
   - Don't screenshot credentials
   - Delete if project abandoned


GETTING HELP
============

If something doesn't work:

1. Check logs:
   - Local: Terminal output
   - Render: Dashboard → Logs tab

2. Common errors:
   - "KeyError: 0" → Missing TgCrypto (fixed on Linux)
   - "ChannelPrivate" → Bot not member of channel
   - "UserNotMember" → Add bot to channel first

3. Test bot is working:
   - Send /start to bot in Telegram
   - Should see menu (if connected)

4. Verify credentials:
   - Check API_ID matches
   - Check BOT_TOKEN is complete
   - Check channel URLs are correct


ADVANCED: CUSTOMIZING SPEED
============================

In forwarder_advanced.py, find:
   await asyncio.sleep(0.3)

Change to:
   await asyncio.sleep(1)      # Slower (safer)
   await asyncio.sleep(0.1)    # Faster (risky)

⚠️ Too fast = Risk of rate limiting!


SUCCESS CHECKLIST
=================

□ API_ID obtained
□ API_HASH obtained
□ Bot token created
□ .env file created (locally)
□ Environment variables set (Render)
□ Bot added to source channel
□ Bot added to destination channel
□ Bot is running
□ /start menu appears
□ Can select channel
□ Topics visible
□ Messages forwarding

Once all checked ✓ → Ready to use!


Ready? Let's go! 🚀

Start with Step 1 above!
"""
