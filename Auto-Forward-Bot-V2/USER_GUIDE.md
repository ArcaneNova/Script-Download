# 📱 AUTO-FORWARD BOT - Complete User Guide

## Full Step-by-Step Instructions from Start to End

---

## ✅ INITIAL SETUP (One-time Setup)

### Step 1: Start the Bot

1. Open Telegram
2. Search for: **@goclassbckup_bot** (or your bot name)
3. Tap **START** button or send `/start`
4. Bot will reply with welcome message

---

### Step 2: Add Your Bot Account (Settings)

1. Send `/settings` command
2. Bot shows menu with options
3. Tap **🤖 My Bots** button
4. Bot asks: "Do you have a bot token?"
5. Two options appear:
   - **✚ Add bot** (if you have a BOT token)
   - **✚ Add User bot** (if you have a USER account session)

**Choose Option A OR B:**

#### **Option A: Adding a Bot Token** (Easier)
1. Get your bot token from [@BotFather](https://t.me/BotFather)
2. Tap **✚ Add bot**
3. Send the bot token
4. Bot will save it ✅

#### **Option B: Adding a User Account** (Better for restricted channels)
1. Run `python sessiongen.py` in terminal
2. Follow the steps to generate a session string
3. Tap **✚ Add User bot**
4. Paste the session string
5. Bot will save it ✅

**Note:** User account sessions bypass more restrictions, but bot tokens are easier.

---

### Step 3: Add Target Channel (Where messages will be sent)

1. Send `/settings` command
2. Tap **📨 My Channels** button
3. Tap **✚ Add Channel**
4. Bot asks: "Send channel link or forward a message from target channel"

**Do ONE of these:**

- **Method 1: Send Channel Link**
  - Type: `t.me/yourchannel` (your target channel username)
  - Or: `https://t.me/yourchannel`
  - Or for private: `t.me/c/123456789`
  
- **Method 2: Forward a Message**
  - Go to your target channel
  - Find any message
  - Forward it to the bot
  - Send it

5. Bot confirms: **"Successfully updated"** ✅

**⚠️ IMPORTANT:** Make sure your bot is **ADMIN** in this channel with permissions:
- Send Messages
- Edit Messages
- Delete Messages

---

## 🚀 MAIN USAGE: FORWARDING MESSAGES

### Step 4: Start Forwarding with `/fwd`

1. Send `/fwd` or `/forward` command
2. Bot shows different scenarios based on your setup

---

### **SCENARIO A: Single Target Channel**

If you added 1 target channel, bot directly asks for source:

```
Bot says: "SET SOURCE CHAT"
"Forward the last message or message link of source chat.
Type 'me' or 'saved' to forward from Saved Messages.
/cancel - cancel this process"
```

**Send ONE of these:**

#### **A1: Paste Message Link (EASIEST)**
- Go to source channel
- Click on any message
- Tap **Share** → **Copy Link**
- Paste the link to bot
- Example: `https://t.me/sourcechannel/12345`

#### **A2: Forward Last Message**
- Go to source channel
- Long-press on the last message you want
- Tap **Forward**
- Forward to the bot
- Bot will read it

#### **A3: From Saved Messages**
- Type: `me` or `saved`
- Bot asks: 
  ```
  SELECT MODE:
  1. batch - Forward existing messages
  2. live - Forward existing and wait for new ones
  ```
- Reply: `1` or `2`
- If `batch`, bot asks how many messages
  - Type a number: `100`
  - Or type: `all`

---

### **SCENARIO B: Multiple Target Channels**

If you added 2+ channels, bot asks which one first:

```
Bot shows buttons with channel names
Choose which channel to send messages to
```

1. Tap the channel name button
2. Then proceed like Scenario A

---

### Step 5: Set Skip Number

```
Bot says: "SET MESSAGE SKIPPING NUMBER"
"Skip messages and forward the rest.
Default = 0 (no skip)"
```

**Send a number:**
- `0` = Forward all messages starting from last
- `5` = Skip first 5 messages, then forward rest
- `10` = Skip first 10, then forward rest

Example: If you choose 5, messages 1-5 are skipped, 6+ are forwarded

---

### Step 6: Review & Confirm

Bot shows confirmation:

```
DOUBLE CHECKING ⚠️

★ YOUR BOT: @botname
★ FROM CHANNEL: Source Channel Name
★ TO CHANNEL: Target Channel Name
★ SKIP MESSAGES: 0

⚠️ Important notes:
- Bot must be admin in TARGET CHAT
- If SOURCE is private, bot must be member or admin
```

**Check everything is correct, then:**

- Tap **✅ Yes** → Start forwarding
- Tap **❌ No** → Cancel and start over

---

### Step 7: Forwarding In Progress

Bot shows progress:

```
📈 Progress: 45%
♻️ Fetched: 450
♻️ Forwarded: 400
♻️ Remaining: 550
⏳ ETA: 5 minutes
```

**Wait until it shows:**
```
🎉 FORWARDING COMPLETED 🥀
```

---

## 📊 OTHER COMMANDS

### `/stats`
Shows bot statistics:
- Total users
- Total bots added
- Total channels added
- Total forwards completed

---

### `/help`
Shows all available commands and what they do

---

### `/cancel`
Stops current forwarding operation

---

### `/settings`
Go back to settings to:
- Change bot
- Add/remove channels
- Set filters
- Set captions
- Configure forwarding options

---

## ⚠️ TROUBLESHOOTING

### Problem: "This is not a forward message"
**Solution:** 
- Make sure you're forwarding from a CHANNEL (not a group)
- Or paste a message link instead: `t.me/channel/123`

---

### Problem: "Cannot access this channel"
**Solution:**
- Bot needs to be MEMBER or ADMIN in target channel
- Add bot to the channel first
- Then try `/settings` → Add Channel again

---

### Problem: "Please Make Bot Admin"
**Solution:**
- Open target channel
- Add bot as admin with these permissions:
  - ✅ Post Messages
  - ✅ Edit Messages
  - ✅ Delete Messages
- Then try `/fwd` again

---

### Problem: "Source chat may be private"
**Solution:**
- If source channel is private:
  - Option 1: Add bot as admin in source channel
  - Option 2: Use a User account (more powerful) - add via `sessiongen.py`
  - Option 3: Paste message link instead of forwarding

---

### Problem: Messages not forwarding
**Solution:**
1. Check if bot is admin in BOTH channels
2. Check if bot has permissions to send/edit messages
3. Try with `/fwd` again
4. If still not working, use `/cancel` and restart

---

## 🎯 QUICK REFERENCE CHECKLIST

Before you start forwarding, verify:

- [ ] Bot token or user session added (`/settings`)
- [ ] Target channel added (`/settings` → My Channels)
- [ ] Bot is ADMIN in target channel
- [ ] Bot has message sending/editing permissions
- [ ] You have source message link OR can forward from source
- [ ] If source is private, bot is member/admin there too

---

## 📌 COMMON WORKFLOWS

### Workflow 1: Backup Channel Messages
```
1. /fwd
2. Paste message link from source
3. Choose target backup channel
4. Set skip to 0
5. Click Yes
6. Wait for completion ✅
```

---

### Workflow 2: Forward from Saved Messages
```
1. /fwd
2. Type: me
3. Choose: batch or live
4. If batch, enter number (e.g., 100)
5. Set skip number
6. Click Yes
7. Messages forward ✅
```

---

### Workflow 3: Auto-Forward to Multiple Channels
```
1. /fwd
2. Paste source link
3. Choose channel 1 (tap button)
4. Set skip 0
5. Click Yes - forwarding starts
6. /fwd again
7. Same source link
8. Choose channel 2 (tap button)
9. Set skip 0
10. Click Yes - second forwarding starts ✅
```

---

## 🔐 PRIVACY & SECURITY

- Bot stores only: Channel IDs, Message links, Forward counts
- Bot does NOT store: Message content, User messages
- All forwarding happens through official Telegram API
- Your session data is stored locally (not on external servers)

---

## 📞 SUPPORT

If you have issues:
1. Check troubleshooting section above
2. Make sure bot is admin in channels
3. Try `/cancel` then `/fwd` again
4. Contact bot admin: [@dev_gagan](https://t.me/dev_gagan)

---

## ✨ SUMMARY

**3 Easy Steps:**
1. `/settings` → Add bot/userbot + target channel
2. `/fwd` → Choose source and destination
3. Confirm → Bot forwards automatically ✅

**That's it!** Now you can forward from restricted channels easily! 🚀

---

**Last Updated:** April 5, 2026  
**Status:** Ready to Use  
**Version:** 2.0 (Complete Rewrite with Link Support)
