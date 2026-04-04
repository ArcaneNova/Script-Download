# Render Deployment Guide

## Quick Start

### 1. Create a Render Account
- Go to https://render.com
- Sign up with your GitHub account (recommended)

### 2. Connect Your Repository
- Fork this repository to your GitHub account
- Go to Render Dashboard → New → Web Service
- Select "Build and deploy from a Git repository"
- Connect your GitHub account and select your fork

### 3. Configure Environment Variables
In the Render dashboard, set the following environment variables:

```
API_ID=35188145
API_HASH=3f725a3cf7a87167a58c4e098c9a1828
BOT_TOKEN=<your_bot_token_here>
DATABASE=<your_mongodb_uri_here>
SOURCE_CHANNEL=https://t.me/+3CoEtU8yo0hhZGVh
DESTINATION_CHANNEL=@gatearshadbackup
```

**Critical:** Update `BOT_TOKEN` and `DATABASE` with your actual values.

### 4. Deploy
- Click "Create Web Service"
- Render will automatically:
  - Install dependencies from `requirements.txt`
  - Build TgCrypto (works on Linux)
  - Start the bot with `python main.py`

### 5. Monitor Logs
- View real-time logs in the Render dashboard
- The bot will auto-forward messages from SOURCE_CHANNEL to DESTINATION_CHANNEL

## What the Bot Does

1. **Connects** to Telegram as a bot using your token
2. **Listens** to the source private channel
3. **Forwards** all new messages to your backup channel automatically

## Troubleshooting

### Bot won't start
- Check that `BOT_TOKEN` and `DATABASE` are set correctly
- View logs in Render dashboard for errors

### Messages not forwarding
- Ensure `SOURCE_CHANNEL` and `DESTINATION_CHANNEL` are correct
- Verify the bot has access to both channels
- Check the bot's permission level

### Database connection errors
- Verify your MongoDB URI is correct
- Ensure your IP is whitelisted in MongoDB Atlas

## Monitoring

The bot includes:
- Error logging to help debug issues
- Auto-retry logic for transient Telegram API failures
- Flood wait handling to respect Telegram rate limits

## Stopping the Bot

Go to your Render service page and click "Suspend" or "Delete" as needed.

## Support

For issues with:
- **Render**: Check https://render.com/docs
- **Pyrogram**: Check https://docs.pyrogram.org
- **This bot**: Review the logs in Render dashboard
