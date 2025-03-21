import os
from typing import Union, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from api.api_models import AdminInsertUserModel, AdminUpdateUserModel
from config import get_settings
from database.models import UserDbModel, UserRoles, ActionsDbModel, MessageDbModel, SessionDbModel

settings = get_settings()

class __Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

class AsyncMongoClient:

    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb://user:pass@mongo:27017")

    async def create_admin(self):
        from api.auth_utils import get_password_hash
        query = {"username": settings.ADMIN_LOGIN}
        admin = await self.client.telegram_db.users.find_one(query)
        if not admin:
            admin = UserDbModel(
                username=settings.ADMIN_LOGIN,
                user_description="admin",
                user_session_id="",
                user_role=UserRoles.admin,
                user_hashed_password=get_password_hash(settings.ADMIN_PASSWORD)
            )
            await self.client.telegram_db.users.insert_one(admin.model_dump())
            
    async def get_user_by_login(self, username: str) -> Union[UserDbModel, None]:
        query = {"username": username}
        user = await self.client.telegram_db.users.find_one(query)
        return UserDbModel.model_validate(user)

    async def get_all_users_by_admin(self) -> List[UserDbModel]:
        users = await self.client.telegram_db.users.find().to_list(None)
        return [UserDbModel.model_validate(user) for user in users]

    async def add_user_by_admin(self, new_user: AdminInsertUserModel) -> Union[str, None]:
        from api.auth_utils import get_password_hash
        query = {"username": new_user.new_username}
        user = await self.client.telegram_db.users.find_one(query)
        if not user:
            new_db_user = UserDbModel(
                username=new_user.new_username,
                user_hashed_password=get_password_hash(new_user.new_user_password),
                user_session_id=new_user.new_user_session_id,
                user_description=new_user.new_user_description,
                user_role=new_user.new_user_role,
                active=new_user.new_user_active
            )
            result = await self.client.telegram_db.users.insert_one(new_db_user.model_dump())
            return str(result.inserted_id)

    async def update_user_by_admin(self, username: str, user_new_data: AdminUpdateUserModel) -> Union[str, None]:
        from api.auth_utils import get_password_hash
        if username == settings.ADMIN_LOGIN:
            return None
        all_users: List[UserDbModel] = await self.get_all_users_by_admin()
        query = {"username": username}
        user = await self.client.telegram_db.users.find_one(query)
        if user and len([item for item in all_users if item.username == user_new_data.updated_username]) == 0:
            existing_user_model = UserDbModel.model_validate(user)
            updated_user = UserDbModel(
                username= existing_user_model.username if user_new_data.updated_username is None else user_new_data.updated_username,
                user_hashed_password=existing_user_model.user_hashed_password if user_new_data.updated_user_password is None else get_password_hash(user_new_data.updated_user_password),
                user_session_id=existing_user_model.user_session_id if user_new_data.updated_user_session_id is None else user_new_data.updated_user_session_id,
                user_description=existing_user_model.user_description if user_new_data.updated_user_description is None else user_new_data.updated_user_description,
                user_role=existing_user_model.user_role if user_new_data.updated_user_role is None else user_new_data.updated_user_role,
                active=existing_user_model.active if user_new_data.updated_user_active is None else user_new_data.updated_user_active
            )
            result = await self.client.telegram_db.users.replace_one({"_id": user["_id"]}, updated_user.model_dump())
            return str(result.upserted_id)

    async def delete_user_by_admin(self, username: str) -> int:
        if username == settings.ADMIN_LOGIN:
            return 0
        query = {"username": username}
        result = await self.client.telegram_db.users.delete_one(query)
        return result.deleted_count

    async def add_new_session(self, session_data: SessionDbModel):
        await self.client.telegram_db.sessions.insert_one(session_data.model_dump())

    async def get_all_sessions_by_admin(self) -> list:
        sessions = await self.client.telegram_db.sessions.find().to_list(None)
        return sessions

    async def get_session_by_id(self, session_id: str):
        return await self.client.telegram_db.sessions.find_one(ObjectId(session_id))

    async def delete_session_by_admin(self, session_id: str) -> int:
        session = await self.get_session_by_id(session_id)
        session_data = SessionDbModel.model_validate(session)
        session_path = f"sessions/{session_data.session_file_name}"
        os.remove(session_path)
        result = await self.client.telegram_db.sessions.delete_one(session)
        return result.deleted_count

    async def get_action_history(self, limit: int, offset: int) -> List[MessageDbModel]:
        result: list = await self.client.telegram_db.messages.find().to_list(None)
        result.reverse()
        filtered_result = result[offset:][:limit]
        return [MessageDbModel.model_validate(item) for item in filtered_result]

    async def safe_message(self, message_action: MessageDbModel):
        await self.client.telegram_db.messages.insert_one(message_action.model_dump())

    async def safe_log_action(self, log_action: ActionsDbModel):
        await self.client.telegram_db.actions.insert_one(log_action.model_dump())
