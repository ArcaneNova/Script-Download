# 🚀 QUICK START CARD

## First Time Setup (2 minutes)

```
1️⃣ Start Bot
   → Search @goclassbckup_bot
   → Tap START

2️⃣ Add Bot Account
   → /settings
   → 🤖 My Bots
   → ✚ Add bot (or ✚ Add User bot)
   → Send token/session

3️⃣ Add Target Channel
   → /settings
   → 📨 My Channels  
   → ✚ Add Channel
   → Send: t.me/yourchannelname
   → ✅ Confirmed

4️⃣ Make Bot Admin
   → Go to target channel
   → Add bot as admin
   → Give permissions: Send, Edit, Delete
```

---

## Using Bot (30 seconds per forward)

```
/fwd

↓ (if multiple channels)
Choose target channel

↓
Paste message link: t.me/source/123
OR
Forward last message
OR  
Type: me/saved

↓
Enter skip number (usually 0)

↓
REVIEW & CLICK YES ✅

↓
BOT FORWARDS AUTOMATICALLY 🎉
```

---

## Input Options

### Source Message (What to copy FROM)

| Option | How | Example |
|--------|-----|---------|
| **Message Link** | Copy from channel | `t.me/channel/12345` |
| **Forward** | Forward message to bot | Long-press → Forward |
| **Saved Messages** | Type text | `me` or `saved` |

### Target Channel (Where to send TO)

| Option | Setup | Check |
|--------|-------|-------|
| **Link** | `t.me/yourname` | Must be admin there |
| **Forward** | Forward a message | Must be admin there |
| **Private** | `t.me/c/12345` | Must be admin there |

---

## Key Numbers

| Setting | Default | Min | Max |
|---------|---------|-----|-----|
| Skip Messages | 0 | 0 | ∞ |
| Batch Messages | All | 1 | 10000 |
| Rate Limit | Auto | - | - |

---

## Bot Commands

```
/start      → Start bot
/fwd        → Forward messages  
/forward    → Same as /fwd
/settings   → Manage bots & channels
/stats      → View statistics
/help       → Get help
/cancel     → Stop operation
/restart    → Restart bot
/resetall   → Clear all data
/broadcast  → Send message to all users
```

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| "Cannot access channel" | Make bot admin |
| "Not a forward message" | Use link: `t.me/channel/123` |
| "Admin not in target" | Add bot to channel + make admin |
| "Private channel access" | Add bot as admin OR use user session |
| "Forwarding stuck" | Send `/cancel` then restart |

---

## Must-Have Checklist ✅

```
Before /fwd:
☑ Bot account added (/settings)
☑ Target channel added (/settings)
☑ Bot is ADMIN in target channel
☑ Have source link OR can forward
```

---

## File/Link Formats That Work

### ✅ Accepted Links
```
t.me/channel/123
https://t.me/channel/123
t.me/c/123456789/456
https://t.me/c/123456789/456
telegram.me/channel/123
telegram.dog/channel/123
```

### ✅ Message Types
```
Text messages
Photos/Images
Videos
Documents/Files
Audio files
Voice messages
Stickers
```

### ❌ NOT Supported
```
Group messages (only channels)
Ephemeral/self-destruct messages
Messages from bots (usually)
```

---

## Pro Tips 💡

1. **Multi-Channel Forwarding**: Run `/fwd` multiple times with same source to send to different targets

2. **Skip Old Messages**: Use skip number to skip already-forwarded messages

3. **Live Mode**: For Saved Messages, choose `live` to keep forwarding new messages

4. **Batch Mode**: Choose `batch` to forward limited number of messages

5. **Check Permissions**: Always verify bot is admin before starting

---

## Performance

- **Speed**: 1-10 messages per second (depends on message size)
- **Limit**: No limit per forward (can do 10,000+)
- **Continuous**: Can run multiple forwards at same time
- **Storage**: All operations stored in database

---

## FAQ

**Q: Can I forward from private channels?**  
A: Yes, if bot is admin there. Or use user session for more power.

**Q: Can I forward to multiple channels at once?**  
A: Run `/fwd` multiple times with same source, pick different targets.

**Q: What happens if bot stops?**  
A: Send `/cancel` then restart `/fwd`. Progress is saved.

**Q: Can I forward without making bot admin?**  
A: No, bot needs admin to send messages to channel.

**Q: Is this legal?**  
A: Yes, it uses official Telegram API and respects channel permissions.

---

## Support Resources

- **Telegram**: [@dev_gagan](https://t.me/dev_gagan)
- **Issues**: GitHub issue tracker
- **Docs**: Check `USER_GUIDE.md` for detailed steps
- **Error**: Send `/help` to bot

---

**Ready? Send `/start` to your bot now!** 🚀

Last Updated: April 5, 2026
