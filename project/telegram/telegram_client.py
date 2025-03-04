from telethon import TelegramClient

from config import get_settings

settings = get_settings()

class TelegramAccount:

    def __init__(self, session_path: str = settings.TELEGRAM_SESSION_PATH):
        self.__channel_client = TelegramClient(
            session=session_path,
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH
        )

    def create_session(self):
        self.__channel_client.start()

    async def get_client(self) -> TelegramClient:
        await self.__channel_client.connect()
        return self.__channel_client
