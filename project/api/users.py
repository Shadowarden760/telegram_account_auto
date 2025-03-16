from datetime import timedelta
from typing import Any, Union, List

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, Body
from fastapi.security import OAuth2PasswordRequestForm
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.types import InputChannel, DocumentAttributeFilename

from api.api_models import (StatusEnum, SendMessageModel, SendMessageModelResponse,
                            SubscribeChannelModel, SubscribeChannelModelResponse,
                            CommentMessageModel, CommentMessageModelResponse,
                            LikeMessageModel, LikeMessageModelResponse)
from api.auth_utils import authenticate_user, create_access_token, get_user
from config import get_settings
from database.database import AsyncMongoClient
from database.models import UserDbModel, ActionsDbModel, ActionsEnum, MessageDbModel
from telegram.telegram_client import TelegramAccount

settings = get_settings()

router = APIRouter()

@router.post("/login", name="login", tags=["default"])
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

@router.post(path="/users/send_message", name="users:send_message", tags=["users"])
async def send_message(message: SendMessageModel = Body(), upload_files: List[UploadFile] = None,
                       user: Union[UserDbModel, None] = Depends(get_user)) -> SendMessageModelResponse:
    account = await TelegramAccount().get_client()
    db = AsyncMongoClient()
    try:
        await account.get_dialogs()
        item = await account.get_entity(message.chat_id)
        if upload_files is not None:
            files_bytes = [await file.read() for file in upload_files]
            file_names = [DocumentAttributeFilename(file.filename) for file in upload_files]
            caption = ["" for _ in upload_files]
            caption[-1] = message.text_message
            result = await account.send_file(entity=item, caption=caption, file=files_bytes)
            action_data = {}
            for i in range(0, len(result)):
                action_data[f"{i}"] = result[i].to_dict()
                await db.safe_message(__get_data_from_message_object(message=result[i]))
            action = ActionsDbModel(
                action_status=True,
                action_type=ActionsEnum.send_message,
                action_data=action_data
            )
            await db.safe_log_action(log_action=action)
            return SendMessageModelResponse(status=StatusEnum.success, message_id=[message.id for message in result])
        else:
            result = await account.send_message(entity=item, message=message.text_message)
            await db.safe_message(__get_data_from_message_object(message=result))
            action = ActionsDbModel(
                action_status=True,
                action_type=ActionsEnum.send_message,
                action_data=result.to_dict()
            )
            await db.safe_log_action(log_action=action)
            return SendMessageModelResponse(status=StatusEnum.success, message_id=[result.id])
    except Exception as ex:
        action = ActionsDbModel(
            action_status=False,
            action_type=ActionsEnum.send_message,
            action_data={"error": f"{ex}"}
        )
        await db.safe_log_action(log_action=action)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )
    finally:
        await account.disconnect()

@router.post(path="/users/subscribe_channel", name="users:subscribe_channel", tags=["users"])
async def subscribe_channel(subscribe: SubscribeChannelModel,
                            user: Union[UserDbModel, None] = Depends(get_user)) -> SubscribeChannelModelResponse:
    account = await TelegramAccount().get_client()
    db = AsyncMongoClient()
    try:
        await account.get_dialogs()
        result = False

        if subscribe.channel_id is None and subscribe.channel_name is None:
            raise RuntimeError("you should provide id or name of channel")
        elif subscribe.channel_id is not None:
            item = await account.get_input_entity(subscribe.channel_id)
            channel = InputChannel(item.channel_id, item.access_hash)
            result = await __subscribe_channel(account=account, channel=channel, subscribe=subscribe.subscribe)
        elif subscribe.channel_name is not None:
            item = await account.get_input_entity(subscribe.channel_name)
            channel = InputChannel(item.channel_id, item.access_hash)
            result = await __subscribe_channel(account=account, channel=channel, subscribe=subscribe.subscribe)

        if result:
            action = ActionsDbModel(
                action_status=True,
                action_type=ActionsEnum.subscribe_channel,
                action_data=result
            )
            await db.safe_log_action(log_action=action)
            return SubscribeChannelModelResponse(
                status=StatusEnum.success, channel_id=str(channel.channel_id),channel_name=subscribe.channel_name
            )
        else:
            action = ActionsDbModel(
                action_status=False,
                action_type=ActionsEnum.subscribe_channel,
                action_data=result
            )
            await db.safe_log_action(log_action=action)
            return SubscribeChannelModelResponse(status=StatusEnum.failure)
    except Exception as ex:
        action = ActionsDbModel(
            action_status=False,
            action_type=ActionsEnum.subscribe_channel,
            action_data={"error": f"{ex}"}
        )
        await db.safe_log_action(log_action=action)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )
    finally:
        await account.disconnect()

@router.post(path="/users/comment_message", name="users:comment_message", tags=["users"])
async def comment_message(comment: CommentMessageModel, user: Union[UserDbModel, None] = Depends(get_user)) -> CommentMessageModelResponse:
    try:
        return CommentMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/users/like_message", name="users:like_message", tags=["users"])
async def like_message(like: LikeMessageModel, user: Union[UserDbModel, None] = Depends(get_user)) -> LikeMessageModelResponse:
    try:
        return LikeMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/users/enable_2fa", name="users:enable_2fa", tags=["users"])
async def enable_2fa(user: Union[UserDbModel, None] = Depends(get_user)) -> Any:
    try:
        return {"status": "ok"}
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.get(path="/users/history", name="users:history", tags=["users"])
async def get_history(offset: int = 0, limit: int = 10, user: Union[UserDbModel, None] = Depends(get_user)) -> dict:
    db = AsyncMongoClient()
    try:
        result = await db.get_action_history(offset=offset, limit=limit)
        action = ActionsDbModel(
            action_type=ActionsEnum.get_history,
            action_data={"offset": offset, "limit": limit},
            action_status=True
        )
        await db.safe_log_action(log_action=action)
        return {"status": "ok", "data": str(result)}
    except Exception as ex:
        action = ActionsDbModel(
            action_type=ActionsEnum.get_history,
            action_data={"offset": offset, "limit": limit},
            action_status=False
        )
        await db.safe_log_action(log_action=action)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )


async def __subscribe_channel(account: TelegramClient, channel: InputChannel, subscribe: bool) -> bool:
    if subscribe:
        await account(JoinChannelRequest(channel))
    else:
        await account(LeaveChannelRequest(channel))
    return True

def __get_data_from_message_object(message) -> MessageDbModel:
    sender_id = str(message.from_id.user_id) if (message.from_id is not None) else ""
    recipient_id = str(message.peer_id.user_id) if (message.peer_id is not None) else ""
    return MessageDbModel(
        message_id=message.id,
        message_text=message.message,
        sender_id=sender_id,
        recipient_id=recipient_id
    )