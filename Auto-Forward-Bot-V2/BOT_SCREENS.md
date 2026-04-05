# 📸 BOT INTERACTION FLOW (What You'll See)

## PART 1: SETUP PHASE

### Screen 1: Start Bot
```
User sends: /start

Bot replies:
"Welcome to Auto-Forward Bot!

This bot helps you forward messages from 
restricted channels to your own channel.

Commands:
/fwd - Forward messages
/settings - Setup bot & channels
/help - Get help"

[START] button disappears
```

---

### Screen 2: Go to Settings
```
User sends: /settings

Bot replies with 4 buttons:
┌─────────────────────┐
│  🤖 My Bots         │
│  📨 My Channels     │
│  ⚙️ Filters          │
│  📝 Caption         │
└─────────────────────┘
```

---

### Screen 3: Add Bot Account
```
User taps: 🤖 My Bots

Bot replies:
"My Bots

You can manage your bots in here"

With options:
┌─────────────────────┐
│ ✚ Add bot           │
│ ✚ Add User bot      │
│ ↩ Back              │
└─────────────────────┘
```

---

### Screen 3A: Add Bot Token
```
User taps: ✚ Add bot

Bot asks:
"Send your bot token from @BotFather"

User sends: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

Bot replies:
✅ "Bot token successfully added to db"
```

---

### Screen 3B: Add User Session
```
User taps: ✚ Add User bot

Bot asks:
"Send your user session string"

User sends: (pastes session from sessiongen.py)

Bot replies:
✅ "Session successfully added to db"
```

---

### Screen 4: Add Target Channel
```
User taps: 📨 My Channels

Bot replies with any existing channels:
[Channel Name 1]
[Channel Name 2]
✚ Add Channel
↩ Back

User taps: ✚ Add Channel

Bot asks:
"SET TARGET CHAT

Forward a message from your target chat 
OR paste the channel link (t.me/channelname)

/cancel - cancel this process"
```

---

### Screen 4A: Option 1 - Paste Link
```
User sends: t.me/mychannel

Bot replies:
✅ "Successfully updated"
```

---

### Screen 4B: Option 2 - Forward Message
```
User:
1. Goes to target channel
2. Finds any message
3. Presses and holds (long-press)
4. Taps "Forward"
5. Forwards to bot

Bot receives forwarded message

Bot replies:
✅ "Successfully updated"
```

---

### Screen 5: Verify Setup
```
User taps: ↩ Back to go back to settings

Settings menu shows:
✅ 🤖 My Bots: @mybotname
✅ 📨 My Channels: My Channel Name

Both are set up! Ready for forwarding.
```

---

## PART 2: FORWARDING PHASE

### Screen 6: Start Forwarding
```
User sends: /fwd

Bot replies:
"Please set a to channel in /settings 
before forwarding"

(if no channels added, this error shows)

OR if channels are added, continues to Screen 7
```

---

### Screen 7A: Choose Target (If Multiple Channels)
```
Bot shows buttons for each channel:
┌──────────────────────┐
│ My Main Channel      │
│ Backup Channel       │
│ Archive Channel      │
│ cancel               │
└──────────────────────┘

User taps: "My Main Channel"

Keyboard disappears
```

---

### Screen 7B: Or Skip (If Single Channel)
```
If only 1 channel added:
Bot automatically uses that channel
(no need to choose)
```

---

### Screen 8: Choose Source
```
Bot asks:
"SET SOURCE CHAT

Forward the last message or message link 
of source chat.

Type 'me' or 'saved' to forward from 
Saved Messages.

/cancel - cancel this process"

(keyboard shows)
```

---

### Screen 8A: Option 1 - Paste Link
```
User sends: https://t.me/sourcechannel/12345

Bot: "Processing..."
```

---

### Screen 8B: Option 2 - Forward Message
```
User:
1. Goes to source channel
2. Finds last message to forward
3. Long-press it
4. Tap "Forward"
5. Forward to bot

Bot: "Processing..."
```

---

### Screen 8C: Option 3 - Saved Messages
```
User sends: me

Bot asks:
"SELECT MODE

Choose the forwarding mode:

1. batch - Forward existing messages
   (you can set limit or choose All)

2. live - Forward existing messages
   and keep waiting for new ones"

User replies: "1" or "batch"

Bot asks:
"NUMBER OF MESSAGES

How many messages?
Enter a number (e.g., 100) or type 'all'"

User sends: "100"
(or "all")
```

---

### Screen 9: Set Skip Number
```
Bot asks:
"SET MESSAGE SKIPPING NUMBER

Skip messages and forward the rest.
Default = 0

eg: You enter 0 = 0 skipped
    You enter 5 = 5 skipped
    You enter 10 = 10 skipped"

User sends: 0

(keyboard shows)
```

---

### Screen 10: Review & Confirm
```
Bot shows:
"DOUBLE CHECKING ⚠️

Before clicking Yes, verify:

★ YOUR BOT: @mybotname
★ FROM CHANNEL: Source Channel Name
★ TO CHANNEL: My Main Channel
★ SKIP MESSAGES: 0

Important:
- Bot must be admin in TARGET CHAT
- If SOURCE is private, bot must be member

[Yes] [No]"

User taps: "Yes"
```

---

### Screen 11: Forwarding Starts
```
Bot shows:
"✅ Forwarding started"

Then shows live progress:

"📈 Percetage: 25%

♻️ Fetched: 250
♻️ Forwarded: 200
♻️ Remaining: 750
♻️ Status: Progressing
⏳ ETA: 12 minutes"

(Updates every 20 messages)
```

---

### Screen 12: Forwarding Complete
```
After all messages forward:

Bot shows:
"🎉 FORWARDING COMPLETED 🥀

Final Statistics:
📊 Total: 1000
✅ Forwarded: 950
⏭ Skipped: 50
🗑 Deleted: 0
📋 Filtered: 0"
```

---

## PART 3: ERROR SCENARIOS

### Error 1: Cannot Access Channel
```
User adds target channel
Bot tries to verify

Bot shows error:
"❌ Cannot access this channel.

Make sure:
- Bot is admin in the channel
- Or you're a member of the channel

Please try again."

Solution: Add bot as admin to channel first
```

---

### Error 2: Bot Not Admin in Target
```
During forwarding:

Bot shows:
"❌ Please Make Your Bot Admin 
In Target Channel With Full Permissions

Permissions needed:
✓ Send Messages
✓ Edit Messages
✓ Delete Messages"

Solution: Go to channel, make bot admin
```

---

### Error 3: Source Channel Access Error
```
During forwarding:

Bot shows:
"❌ Source chat may be a private channel/group.

Solutions:
1. Use userbot (user must be member there)
2. Make your bot admin in source channel
3. Try sending just the message link"
```

---

### Error 4: Invalid Link
```
User sends: "this is not a link"

Bot shows:
"❌ Invalid message link!

Use format:
- t.me/channel/123
- t.me/c/ID/123
- Or forward a message from the source"
```

---

## PART 4: REPEAT FORWARDING

### After First Forward Complete
```
User can:

1. Send /fwd again to forward different source
   
2. Send /fwd with same source to different target
   
3. Send /cancel to abort current operation
   
4. Send /stats to check forwarding count
   
5. Send /settings to change bot or channels
```

---

## FULL FLOW DIAGRAM

```
START (/start)
  ↓
SETTINGS (/settings)
  ↓
SET BOT (Add token or session)
  ↓
SET CHANNEL (Add target channel)
  ↓
FORWARD (/fwd)
  ├─ Choose target (if multiple)
  ├─ Choose source (link/forward/saved)
  ├─ Set skip number
  ├─ Review confirmation
  └─ Start forwarding
  ↓
PROGRESS (Real-time updates)
  ↓
COMPLETE (Shows statistics)
  ↓
REPEAT (Send /fwd again)
```

---

## TIME ESTIMATES

| Action | Time |
|--------|------|
| Setup Bot | 1 minute |
| Add Channel | 30 seconds |
| First Forward | 2-5 minutes |
| Next Forward | 1 minute |
| 1000 Messages | 10-30 minutes |
| 10000 Messages | 1-3 hours |

---

## MESSAGE COUNT Reference

```
Speed varies by:
- Message size (text vs media)
- Internet speed
- Telegram server load
- Rate limiting

Typical speeds:
- Text only: 10-20/sec
- With images: 2-5/sec
- With videos: 1-3/sec
- Mixed: 5-10/sec
```

---

**Now you know exactly what to expect!** 🎯

Step through this guide while using the bot to understand every screen and message you'll see.

Last Updated: April 5, 2026
