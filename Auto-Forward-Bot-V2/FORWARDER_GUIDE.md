# Telegram Topic-Based Message Forwarder Bot

A powerful Telegram bot that forwards all messages from a specific channel topic to your backup channel, preserving the exact sequence and supporting all media types.

## Features

✅ **Multi-Topic Support**
- Select source channel with multiple topics
- View all available topics in a channel
- Forward all messages from a specific topic in exact sequence

✅ **Complete Media Support**
- Text messages
- Videos
- Documents (PDF, ZIP, etc.)
- Photos
- Audio files
- Voice messages
- Video notes
- Stickers

✅ **Real-Time Status Tracking**
- Live progress updates
- Message count tracking
- Success/failure statistics
- Forwarding history database

✅ **User-Friendly Interface**
- Interactive button-based menu
- No command typing required
- Visual progress indicators
- Topic selection with icons

✅ **Sequence Preservation**
- Messages forwarded in exact original order (oldest first)
- Maintains message timestamps
- All media and content preserved

## How to Use

### 1. Start the Bot
```
/start
```

### 2. Select Source Channel
- Click "📥 Select Source Channel"
- Send the channel URL in one of these formats:
  - `https://t.me/c/3895961049/` (public/private channel)
  - `https://t.me/+3CoEtU8yo0hhZGVh` (private invite link)
  - `@channelname` (public channel username)

### 3. Select a Topic
- After connecting, available topics will be displayed
- Click on a topic to start forwarding all its messages

### 4. Monitor Status
- Watch real-time progress updates
- See message count and type
- Track forwarding success/failures

### 5. View Status & History
- Use "📊 View Status" button for overview
- Use "📋 Forwarding History" to see past forwarding sessions

## Installation & Deployment

### Local Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/Auto-Forward-Bot-V2.git
cd Auto-Forward-Bot-V2
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file:**
```env
API_ID=YOUR_API_ID
API_HASH=YOUR_API_HASH
BOT_TOKEN=YOUR_BOT_TOKEN
DATABASE=mongodb+srv://username:password@cluster.mongodb.net/telegram_forwarder
DESTINATION_CHANNEL=@your_backup_channel
BOT_OWNER_ID=YOUR_TELEGRAM_ID
```

5. **Run the bot:**
```bash
python forwarder_advanced.py
```

### Deploy on Render.com

1. **Fork this repository** to your GitHub account

2. **Create a new Web Service on Render:**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service:**
   - Name: `telegram-forwarder`
   - Environment: `Python 3.11`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python forwarder_advanced.py`
   - Plan: Free tier is fine

4. **Add Environment Variables:**
   In Render dashboard, set:
   - `API_ID` - Your Telegram API ID
   - `API_HASH` - Your Telegram API Hash
   - `BOT_TOKEN` - Your bot token
   - `DATABASE` - MongoDB URI (optional, uses in-memory if not set)
   - `DESTINATION_CHANNEL` - Your backup channel
   - `BOT_OWNER_ID` - Your Telegram ID

5. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)
   - Bot will start automatically

### Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Sign in with your Telegram account
3. Go to "API development tools"
4. Create a new application
5. Copy `API_ID` and `API_HASH`

### Create a Bot Token

1. Chat with @BotFather on Telegram
2. Send `/newbot`
3. Follow the prompts
4. Copy your bot token

## Database Setup (MongoDB)

### Free MongoDB Atlas Cluster:
1. Go to https://www.mongodb.com/cloud/atlas
2. Create account and log in
3. Create a new cluster (free tier available)
4. Create a database user
5. Get connection URI: `mongodb+srv://username:password@cluster.mongodb.net/mydb`
6. Set this as `DATABASE` environment variable

**Note:** Without database, the bot still works but won't track history. All forwarding sessions use in-memory storage.

## URL Format Guide

### Channel URL Examples:
```
Public Channel ID: https://t.me/c/3895961049/
This becomes channel ID: -1003895961049

Private Invite Link: https://t.me/+3CoEtU8yo0hhZGVh
Keep as-is for invite links

Public Channel: @mychannel
Use the @username directly
```

### Message URL Structure:
```
https://t.me/c/3895961049/4129/9675
         ^                ^    ^
    Channel ID         Topic  Message ID
```

## Troubleshooting

### Bot Can't Access Channel
- Make sure the bot is a **member** of the source channel
- For private channels, the bot needs to be added manually
- For invite links, make sure the link is valid

### No Topics Found
- Channel must have **Topics** (Forums) enabled
- This is only available in supergroups with topics feature
- Check if channel actually has topics enabled

### Messages Not Forwarding
- Check that bot has permission to send messages in destination channel
- Ensure bot is not muted/restricted
- Check logs for specific error messages

### Slow Forwarding Speed
- Telegram enforces rate limits (anti-spam)
- Forwarding adds slight delays between messages
- This is intentional for stability
- Adjust delays in code if needed (careful with rate limits!)

## Configuration Options

Edit `forwarder_advanced.py` to customize:

```python
# Rate limiting between messages
await asyncio.sleep(0.3)  # Increase if hitting rate limits

# Logging level
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for verbose logs

# Maximum messages per topic (default: 10000)
async for msg in client.get_chat_history(channel_id, limit=10000):
```

## API Reference

### Main Commands

```
/start           - Show main menu
/help            - Show help information
```

### Inline Buttons

```
📥 Select Source Channel  - Choose channel to forward from
📊 View Status            - See overall forwarding status
📋 Forwarding History     - View past forwarding sessions
📤 Forward Topic          - Start forwarding selected topic
❓ Help                   - Show help
```

## Performance

- **Forwarding Speed:** ~200-300 messages/minute (limited by Telegram)
- **Memory Usage:** ~50-100 MB
- **Database:** Optional (works without MongoDB)
- **Concurrent Topics:** Can queue multiple topics

## Limitations

1. **Telegram Rate Limits:** ~1-2 messages per second max
2. **API Limits:** Max 30 requests per second per user
3. **Message Age:** Can only forward existing messages
4. **File Size:** Telegram's file size limits apply (4GB max for bot)
5. **Topic Access:** Must be member of topic-enabled channel

## Security

- Bot token is stored securely in environment variables
- MongoDB connection string encrypted in transit
- No messages stored locally
- All operations logged for audit

## Support

For issues:
1. Check logs: `cat forwarder_bot.log`
2. Check Render logs on dashboard
3. Make sure all environment variables are set
4. Verify bot is member of source channel

## License

MIT License - feel free to use and modify

## Tips & Best Practices

✅ **DO:**
- Add bot to channel BEFORE starting forwarding
- Test with a small topic first
- Monitor logs during first run
- Keep backup of important messages

❌ **DON'T:**
- Change destination channel mid-forwarding
- Stop bot while forwarding (may lose position)
- Use bot token in public places
- Share database credentials

## Advanced Usage

### Custom Message Filtering
Edit `forwarder_advanced.py` to filter specific message types:
```python
# Skip forwarding documents
if msg.document:
    continue

# Only forward videos
if not msg.video:
    continue
```

### Custom Rate Limiting
```python
# Adjust delay between messages
await asyncio.sleep(1)  # Slower
await asyncio.sleep(0.1)  # Faster (risky)
```

### Multiple Instances
Run multiple bots with different destination channels:
```bash
DESTINATION_CHANNEL=@channel1 python forwarder_advanced.py
DESTINATION_CHANNEL=@channel2 python forwarder_advanced.py
```

## Changelog

### v2.0 - Advanced Features
- Topic-based forwarding
- Real-time progress tracking
- Database integration
- Enhanced error handling
- Improved UI/UX

### v1.0 - Initial Release
- Basic forwarding functionality
- Channel support

---

**Need help?** Check the [README](#) or open an issue on GitHub.

Made with ❤️ for Telegram enthusiasts
