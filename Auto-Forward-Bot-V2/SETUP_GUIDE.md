# Save Restricted Bot - Setup Guide

This is a Telegram Bot that downloads and forwards restricted content from private/restricted Telegram channels.

## Prerequisites

- Python 3.8+
- A Telegram account
- A Telegram bot token (from @BotFather)

## Installation Steps

### 1. Install Dependencies

The required packages are already installed:
- `pyrogram` - Telegram client library
- `flask` - Web framework (for deployment)
- `tgcrypto` - Optional encryption library (for better performance)

If you need to reinstall, run:
```bash
pip install -r requirements.txt
```

### 2. Get Your Telegram Credentials

You need to obtain the following from https://my.telegram.org:

#### API ID and API Hash
1. Go to https://my.telegram.org/apps
2. Log in with your Telegram account
3. Create a new application
4. You'll receive:
   - **API ID** - A numeric value
   - **API Hash** - A string value

#### Bot Token
1. Open Telegram and search for **@BotFather**
2. Send `/start` and follow the instructions
3. Send `/newbot` to create a new bot
4. Choose a name and username
5. BotFather will provide your **Bot Token**

#### Session String (for Account Access)
To access restricted content, the bot needs to use your personal account session. To generate a session string:

1. Go to: https://gist.github.com/bipinkrish/0940b30ed66a5537ae1b5aaaee716897#file-main-py
2. Copy the script provided
3. Run it locally in this directory:
   ```bash
   python generate_session.py
   ```
4. It will prompt you to enter your phone number and authentication code
5. Copy the generated session string

**Alternative:** You can leave `STRING` as `null` to use only the bot (without account access for private chats).

### 3. Configure the Bot

Edit `config.json` and add your credentials:

```json
{
    "TOKEN": "your_bot_token_here",
    "ID": "your_api_id_here",
    "HASH": "your_api_hash_here",
    "STRING": "your_session_string_here_or_null"
}
```

**Or use Environment Variables:**

Set these as environment variables instead of using config.json:
```bash
set TOKEN=your_bot_token
set ID=your_api_id
set HASH=your_api_hash
set STRING=your_session_string
```

### 4. Run the Bot

#### Local Development
```bash
cd "d:\Telegram 2026\Script Download\Auto-Forward-Bot-V2"
python main.py
```

#### With Flask Web Server (for deployment)
```bash
python app.py
```

#### Production (Heroku/similar platforms)
- Uses `Procfile` for deployment configuration
- Flask server runs on port 5000 (or PORT environment variable)

## Bot Usage

### For Public Chats
Simply send the post link:
```
https://t.me/channelname/123
```

### For Private Chats
First send the invite link (only needed once):
```
https://t.me/+xxxxx
```
Then send the post links:
```
https://t.me/c/123456/456
```

### For Bot Chats
Send the bot message link:
```
https://t.me/b/botusername/4321
```

### For Multiple Posts
Use the "from - to" format:
```
https://t.me/channelname/1001-1010
https://t.me/c/123456/101-120
```

## File Structure

```
Auto-Forward-Bot-V2/
├── main.py           # Main bot logic
├── app.py            # Flask web server
├── config.json       # Configuration file (edit this with your credentials)
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker configuration
├── Procfile          # Heroku deployment configuration
└── README.md         # Original project README
```

## Troubleshooting

### Import Errors
If you get import errors, make sure all packages are installed:
```bash
pip install pyrogram flask
```

### Session String Issues
- Make sure your session string is valid and not expired
- If you get an authentication error, regenerate the session string
- For private chats, ensure your account is already a member or has been invited

### Connection Issues
- Check your internet connection
- Make sure Telegram is not blocked in your region
- Try using a VPN if Telegram access is restricted

### Bot Not Responding
- Make sure the bot token is correct
- Verify the bot is running: check console for error messages
- Ensure your Telegram account hasn't been restricted

## Notes

- The bot downloads restricted content and forwards it to you
- Private chats require account session access
- Downloaded files are cached temporarily
- Always respect copyright and Telegram's Terms of Service
- Be cautious with what content you request to download

## Environment Variables

Instead of editing `config.json`, you can set environment variables:

| Variable | Description |
|----------|-------------|
| `TOKEN` | Telegram bot token from @BotFather |
| `ID` | API ID from my.telegram.org |
| `HASH` | API Hash from my.telegram.org |
| `STRING` | Session string for account access (optional) |
| `PORT` | Port for Flask server (default: 5000) |

## Support

For issues with the original project, visit: https://github.com/bipinkrish/Save-Restricted-Bot

## Security Notes

- ⚠️ **Never share your session string, API hash, or bot token**
- Don't commit these credentials to version control
- Use environment variables for production deployments
- Consider using a secure password manager to store credentials
