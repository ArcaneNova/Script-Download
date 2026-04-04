"""
Minimal config for standalone forwarder bot.
Reads from environment variables only - no database needed.
"""
from os import environ

API_ID = int(environ.get("API_ID", "0"))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
SOURCE_CHANNEL = environ.get("SOURCE_CHANNEL", "")
DESTINATION_CHANNEL = environ.get("DESTINATION_CHANNEL", "")
DATABASE_URI = environ.get("DATABASE", "")

# Validate critical config
if not all([API_ID, API_HASH, BOT_TOKEN, SOURCE_CHANNEL, DESTINATION_CHANNEL]):
    import logging
    logging.error("Missing required environment variables!")
    import sys
    sys.exit(1)
