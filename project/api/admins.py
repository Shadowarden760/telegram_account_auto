import os
from typing import Union

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile

from api.auth_utils import get_user
from api.api_models import AdminActionResponse, StatusEnum, AdminInsertUserModel, AdminUpdateUserModel
from database.database import AsyncMongoClient
from database.models import UserDbModel, UserRoles

router = APIRouter()


@router.get(path="/admins/admin_get_all_users", name="admins:get_all_users", tags=["admins"],
            description="Get all users (operators and admins) information"
            )
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

@router.post(path="/admins/admin_create_user", name="admins:create_user", tags=["admins"],
             description="Create operator or admin"
             )
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

@router.post(path="/admins/admin_update_user", name="admins:update_user", tags=["admins"],
             description="Update operator or admin information including changing active status"
             )
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

@router.post(path="/admins/admin_delete_user", name="admins:delete_user", tags=["admins"],
             description="Delete operators and admin"
             )
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

@router.post(path="/admins/add_session", name="admins:add_session", tags=["admins"],
             description="Add new session file to system"
             )
async def admin_add_session(session_file: UploadFile, user: Union[UserDbModel, None] = Depends(get_user)):
    try:
        if user.user_role == UserRoles.admin and user.active:
            if session_file is not None:
                session_name = f"sessions/{session_file.filename}"
                with open(session_name, "wb") as file:
                    file.write(session_file.file.read())
                return AdminActionResponse(status=StatusEnum.success, data={"session_name": session_file.filename})
            else:
                return AdminActionResponse(status=StatusEnum.failure, data={"error": "file is empty"})
        else:
            return AdminActionResponse(status=StatusEnum.failure, data={"error": "you are not admin or disabled admin"})
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.get(path="/admins/get_available_sessions", name="admins:get_available_sessions", tags=["admins"],
             description="Get available sessions' names"
             )
async def admin_add_session(user: Union[UserDbModel, None] = Depends(get_user)):
    try:
        if user.user_role == UserRoles.admin and user.active:
            sessions = os.listdir("sessions")
            return AdminActionResponse(status=StatusEnum.success, data={"sessions": sessions})
        else:
            return AdminActionResponse(status=StatusEnum.failure, data={"error": "you are not admin or disabled admin"})
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )


@router.post(path="/admins/delete_session", name="admins:delete_session", tags=["admins"],
             description="Delete session file from system"
             )
async def admin_add_session(session_name: str, user: Union[UserDbModel, None] = Depends(get_user)):
    try:
        if user.user_role == UserRoles.admin and user.active:
            session_path = f"sessions/{session_name}"
            os.remove(session_path)
            return AdminActionResponse(status=StatusEnum.success, data={"deleted": session_name})
        else:
            return AdminActionResponse(status=StatusEnum.failure, data={"error": "you are not admin or disabled admin"})
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )