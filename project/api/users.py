from datetime import timedelta
from typing import Any, Union

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.api_models import (StatusEnum, SendMessageModel, SendMessageModelResponse,
                            SubscribeChannelModel, SubscribeChannelModelResponse,
                            CommentMessageModel, CommentMessageModelResponse,
                            LikeMessageModel, LikeMessageModelResponse,
                            MessageHistoryModel)
from config import get_settings
from database.models import UserDbModel
from utils.auth_utils import authenticate_user, create_access_token, get_user

settings = get_settings()

router = APIRouter()

@router.post("/login", name="login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user: Union[UserDbModel, None] = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post(path="/send_message", name="users:send_message")
async def send_message(message: SendMessageModel, user: Union[UserDbModel, None] = Depends(get_user)) -> SendMessageModelResponse:
    try:
        return SendMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/subscribe_channel", name="users:subscribe_channel")
async def subscribe_channel(subscribe: SubscribeChannelModel, user: Union[UserDbModel, None] = Depends(get_user)) -> SubscribeChannelModelResponse:
    try:
        if subscribe.channel_id is None and subscribe.channel_name is None:
            raise RuntimeError("you should provide id or name of channel")
        return SubscribeChannelModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/comment_message", name="users:comment_message")
async def comment_message(comment: CommentMessageModel, user: Union[UserDbModel, None] = Depends(get_user)) -> CommentMessageModelResponse:
    try:
        return CommentMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/like_message", name="users:like_message")
async def like_message(like: LikeMessageModel, user: Union[UserDbModel, None] = Depends(get_user)) -> LikeMessageModelResponse:
    try:
        return LikeMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/enable_2fa", name="users:enable_2fa")
async def enable_2fa(user: Union[UserDbModel, None] = Depends(get_user)) -> Any:
    try:
        return {"status": "ok"}
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.get(path="/history", name="users:history")
async def get_history(filters: MessageHistoryModel, user: Union[UserDbModel, None] = Depends(get_user)) -> Any:
    try:
        return {"status": "ok"}
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )
