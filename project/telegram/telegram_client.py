from pathlib import Path

from telethon import TelegramClient

from config import get_settings

settings = get_settings()

class TelegramAccount:

    def __init__(self, session_file_name: str):
        self.__channel_client = TelegramClient(
            session= str(Path(f"./sessions/{session_file_name}").absolute()),
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH
        )

    def create_session(self):
        self.__channel_client.start()

    async def connect_client(self):
        await self.__channel_client.connect()

    async def get_client(self) -> TelegramClient:
        await self.__channel_client.connect()
        return self.__channel_client
