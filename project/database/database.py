from motor.motor_asyncio import AsyncIOMotorClient

from config import get_settings
from utils.auth_utils import get_password_hash
from .models import UserDbModel

settings = get_settings()


class __Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

class AsyncMongoClient(__Singleton):

    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb://user:pass@mongo:27017")

    async def create_admin(self):
        query = {"username": settings.ADMIN_LOGIN}
        admin = await self.client.telegram_db.users.find_one(query)
        if not admin:
            admin = UserDbModel(
                username=settings.ADMIN_LOGIN,
                user_description="admin",
                user_hashed_password=get_password_hash(settings.ADMIN_PASSWORD)
            )
            result = await self.client.telegram_db.users.insert_one(admin.model_dump())
            print(result.inserted_id)

