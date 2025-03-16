from typing import Union

from fastapi import APIRouter, HTTPException, status, Depends

from api.auth_utils import get_user
from api.api_models import AdminActionResponse, StatusEnum, AdminInsertUserModel, AdminUpdateUserModel
from database.database import AsyncMongoClient
from database.models import UserDbModel, UserRoles

router = APIRouter()


@router.get(path="/admins/admin_get_all_users", name="admins:get_all_users", tags=["admins"])
async def admin_get_all_users(user: Union[UserDbModel, None] = Depends(get_user)) -> AdminActionResponse:
    try:
        if user.user_role == UserRoles.admin and user.active:
            db = AsyncMongoClient()
            all_users = await db.get_all_users_by_admin()
            return AdminActionResponse(status=StatusEnum.success, data={"all_users": all_users})
        else:
            return AdminActionResponse(status=StatusEnum.failure, data={"error": "you are not admin or disabled admin"})
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/admins/admin_create_user", name="admins:create_user", tags=["admins"])
async def admin_create_user(new_user: AdminInsertUserModel,
                            user: Union[UserDbModel, None] = Depends(get_user)) -> AdminActionResponse:
    try:
        if user.user_role == UserRoles.admin and user.active:
            db = AsyncMongoClient()
            new_id = await db.create_user_by_admin(new_user=new_user)
            return AdminActionResponse(status=StatusEnum.success, data={"new_user_id": new_id})
        else:
            return AdminActionResponse(status=StatusEnum.failure, data={"error": "you are not admin or disabled admin"})
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/admins/admin_update_user", name="admins:update_user", tags=["admins"])
async def admin_update_user(username: str, new_user_data: AdminUpdateUserModel, user: Union[UserDbModel, None] = Depends(get_user)) -> AdminActionResponse:
    try:
        if user.user_role == UserRoles.admin and user.active:
            db = AsyncMongoClient()
            user_id = await db.update_user_by_admin(username=username, user_new_data=new_user_data)
            return AdminActionResponse(status=StatusEnum.success, data={"user_id": user_id})
        else:
            return AdminActionResponse(status=StatusEnum.failure, data={"error": "you are not admin or disabled admin"})
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/admins/admin_delete_user", name="admins:delete_user", tags=["admins"])
async def admin_delete_user(username: str, user: Union[UserDbModel, None] = Depends(get_user)) -> AdminActionResponse:
    try:
        if user.user_role == UserRoles.admin and user.active:
            db = AsyncMongoClient()
            delete_count = await db.delete_user_by_admin(username=username)
            return AdminActionResponse(status=StatusEnum.success, data={"delete_count": delete_count})
        else:
            return AdminActionResponse(status=StatusEnum.failure, data={"error": "you are not admin or disabled admin"})
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )