from decouple import config as env

class Config:
    API_ID = env("API_ID", default="577678")
    API_HASH = env("API_HASH", default="d2c6e01uuiuiouioiuiou0fc6d7a1be")
    BOT_TOKEN = env("BOT_TOKEN", default="70955...")
    BOT_SESSION = env("BOT_SESSION", default="bot")
    DATABASE_URI = env("DATABASE", default="mongodb+srv://chhjgjkkjhkjhkjh@cluster0.xowzpr4.mongodb.net/")
    DATABASE_NAME = env("DATABASE_NAME", default="forward-bot")
    BOT_OWNER_ID = [int(id) for id in env("BOT_OWNER_ID", default='6964148334').split()]
    SOURCE_CHANNEL = env("SOURCE_CHANNEL", default=None)
    DESTINATION_CHANNEL = env("DESTINATION_CHANNEL", default=None)

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
    
