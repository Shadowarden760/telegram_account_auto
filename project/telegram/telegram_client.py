from pathlib import Path

from telethon import TelegramClient

class TelegramAccount:

    def __init__(self, session_file_name: str, app_id: int, app_hash: str):
        self.__channel_client = TelegramClient(
            session= str(Path(f"./sessions/{session_file_name}").absolute()),
            api_id=app_id,
            api_hash=app_hash
        )

    def create_session(self):
        self.__channel_client.start()

    async def connect_client(self):
        await self.__channel_client.connect()

    async def get_client(self) -> TelegramClient:
        await self.__channel_client.connect()
        return self.__channel_client
