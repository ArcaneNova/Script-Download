import re
from typing import Optional, Tuple

def parse_telegram_link(link: str) -> Optional[Tuple[int, int]]:
    """
    Parse a Telegram message link and extract chat_id and message_id.
    
    Supported formats:
    - https://t.me/channel_name/123
    - https://t.me/c/123456789/456
    - t.me/channel_name/123
    - https://telegram.me/channel_name/123
    - https://telegram.dog/channel_name/123
    
    Returns: (chat_id, message_id) or None if invalid
    """
    if not link:
        return None
    
    # Clean up the link
    link = link.strip().replace("?single", "").replace("?thread=", "&thread=")
    
    # Match pattern: (https://)?(t.me|telegram.me|telegram.dog)(/c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)
    pattern = r"(https?://)?(t\.me|telegram\.me|telegram\.dog)(/c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)"
    match = re.match(pattern, link)
    
    if not match:
        return None
    
    chat_identifier = match.group(4)  # Either numeric or username
    message_id = int(match.group(5))
    
    # If it's a private channel (starts with /c/), convert to proper chat_id
    if match.group(3) == "/c/":
        chat_id = int("-100" + chat_identifier)
    # If it's numeric without /c/, it's a private channel too
    elif chat_identifier.isdigit():
        chat_id = int("-100" + chat_identifier)
    # If it's a username, keep it as-is (Telegram accepts both formats)
    else:
        chat_id = chat_identifier
    
    return (chat_id, message_id)


def parse_channel_link(link: str):
    """
    Parse a Telegram channel/group link and extract chat_id.
    
    Supported formats:
    - https://t.me/channel_name
    - https://t.me/c/123456789
    - t.me/channel_name
    
    Returns: chat_id (int for /c/ format, str for username) or None if invalid
    """
    if not link:
        return None
    
    link = link.strip().rstrip("/")
    
    # Match pattern: (https://)?(t.me|telegram.me|telegram.dog)(/c/)?(\d+|[a-zA-Z_0-9]+)$
    pattern = r"(https?://)?(t\.me|telegram\.me|telegram\.dog)(/c/)?([a-zA-Z_0-9]+)$"
    match = re.match(pattern, link)
    
    if not match:
        return None
    
    chat_identifier = match.group(4)
    
    # If it's a private channel (/c/), convert to proper chat_id
    if match.group(3) == "/c/":
        return int("-100" + chat_identifier)
    # If it's numeric without /c/, it's still a private channel
    elif chat_identifier.isdigit():
        return int("-100" + chat_identifier)
    # If it's a username, keep it
    else:
        return chat_identifier
