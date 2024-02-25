import os
from dotenv import load_dotenv

load_dotenv()

class Telegram:
    API_ID = os.getenv("TelegramApiId")
    API_HASH = os.getenv("TelegramApiHash")
    USERNAME = os.getenv("TelegramUsername")
    LISTENER_CHANNELS = os.getenv("TelegramListenerChannels").split(",") 
    CANAIS_FILTRADOS = os.getenv("TelegramFilteredChannels").split(",")
