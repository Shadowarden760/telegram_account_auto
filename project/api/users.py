import os
from typing import Union, List

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, Body
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import InputChannel, PeerChannel, ReactionEmoji

from api.api_models import (StatusEnum, SendMessageModel, SendMessageModelResponse,
                            SubscribeChannelModel, SubscribeChannelModelResponse,
                            CommentMessageModel, CommentMessageModelResponse,
                            LikeMessageModel, LikeMessageModelResponse, GetHistoryModelResponse, TwoFAModelResponse,
                            TwoFAModel)
from api.auth_utils import get_user
from database.database import AsyncMongoClient
from database.models import UserDbModel, ActionsDbModel, ActionsEnum, MessageDbModel
from telegram.telegram_client import TelegramAccount

router = APIRouter()

@router.post(path="/users/send_message", name="users:send_message", tags=["users"],
             description="Send text message with file or files of different formats(images, videos and others)"
             )
async def send_message(message: SendMessageModel = Body(), upload_files: List[UploadFile] = None,
                       user: Union[UserDbModel, None] = Depends(get_user)) -> SendMessageModelResponse:
    account = await TelegramAccount(session_file_name=user.user_session).get_client()
    db = AsyncMongoClient()
    try:
        await account.get_dialogs()
        item = await account.get_entity(message.chat_id)
        if upload_files is not None:
            file_names = [f"temp/{user.username}/{file.filename}" for file in upload_files]
            for i in range (0, len(upload_files)):
                with open(file_names[i], "wb") as temp_file:
                    temp_file.write(upload_files[i].file.read())
            caption = ["" for _ in upload_files]
            caption[-1] = message.text_message
            result = await account.send_file(entity=item, caption=caption, file=file_names)
            for file in file_names:
                os.remove(file)
            action_data = {}
            for i in range(0, len(result)):
                action_data[f"{i}"] = result[i].to_dict()
                await db.safe_message(__get_data_from_message_object(
                    message=result[i], if_channel=message.if_channel, sender_username=user.username)
                )
            action = ActionsDbModel(
                action_status=True,
                action_type=ActionsEnum.send_message,
                action_data=action_data
            )
            await db.safe_log_action(log_action=action)
            return SendMessageModelResponse(status=StatusEnum.success, message_id=[message.id for message in result])
        else:
            result = await account.send_message(entity=item, message=message.text_message)
            await db.safe_message(__get_data_from_message_object(
                message=result, if_channel=message.if_channel, sender_username=user.username)
            )
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

@router.post(path="/users/subscribe_channel", name="users:subscribe_channel", tags=["users"],
             description="Subscribe channel by name (t.me/something) or id"
             )
async def subscribe_channel(subscribe_data: SubscribeChannelModel,
                            user: Union[UserDbModel, None] = Depends(get_user)) -> SubscribeChannelModelResponse:
    account = await TelegramAccount(session_file_name=user.user_session).get_client()
    db = AsyncMongoClient()
    try:
        await account.get_dialogs()

        if subscribe_data.channel_id is None and subscribe_data.channel_name is None:
            raise RuntimeError("you should provide id or name of channel")
        elif subscribe_data.channel_name is not None:
            item = await account.get_entity(subscribe_data.channel_name)
            channel = InputChannel(item.id, item.access_hash)
        else:
            item = await account.get_entity(PeerChannel(channel_id=subscribe_data.channel_id))
            channel = InputChannel(item.id, item.access_hash)

        result = await __subscribe_channel(account=account, channel=channel, subscribe=subscribe_data.subscribe_flag)
        if result:
            action = ActionsDbModel(
                action_status=True,
                action_type=ActionsEnum.subscribe_channel,
                action_data={"channel_name": item.username, "channel_id": item.id,
                             "result": result, "subscribe": subscribe_data.subscribe_flag}
            )
            await db.safe_log_action(log_action=action)
            return SubscribeChannelModelResponse(
                status=StatusEnum.success, channel_id=str(item.id),channel_name=item.username
            )
        else:
            action = ActionsDbModel(
                action_status=False,
                action_type=ActionsEnum.subscribe_channel,
                action_data={"channel_name": item.username, "channel_id": item.id,
                             "result": result, "subscribe": subscribe_data.subscribe_flag}
            )
            await db.safe_log_action(log_action=action)
            return SubscribeChannelModelResponse(
                status=StatusEnum.failure, channel_id=str(item.id), channel_name=item.username
            )
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

@router.post(path="/users/comment_message", name="users:comment_message", tags=["users"],
             description="Comment channel message with plain text"
             )
async def comment_message(comment_data: CommentMessageModel,
                          user: Union[UserDbModel, None] = Depends(get_user)) -> CommentMessageModelResponse:
    account = await TelegramAccount(session_file_name=user.user_session).get_client()
    db = AsyncMongoClient()
    try:
        await account.get_dialogs()
        channel = await account.get_input_entity(comment_data.channel_id)
        result = await account.send_message(entity=channel, message=comment_data.comment, comment_to=comment_data.message_id)
        action = ActionsDbModel(
            action_status=True,
            action_type=ActionsEnum.comment_message,
            action_data=result.to_dict()
        )
        await db.safe_log_action(log_action=action)
        return CommentMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        action = ActionsDbModel(
            action_status=False,
            action_type=ActionsEnum.comment_message,
            action_data={"error": f"{ex}"}
        )
        await db.safe_log_action(log_action=action)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )
    finally:
        await account.disconnect()

@router.post(path="/users/like_message", name="users:like_message", tags=["users"],
             description="Like message with emoticon"
             )
async def like_message(like_data: LikeMessageModel, user: Union[UserDbModel, None] = Depends(get_user)) -> LikeMessageModelResponse:
    account = await TelegramAccount(session_file_name=user.user_session).get_client()
    db = AsyncMongoClient()
    try:
        await account.get_dialogs()
        item = await account.get_entity(like_data.chat_id)
        await __sent_reaction(account=account, message_id=like_data.message_id, peer=item, emoticon=like_data.emoticon)
        action = ActionsDbModel(
            action_status=True,
            action_type=ActionsEnum.like_message,
            action_data={"chat_id": like_data.chat_id, "message_id": like_data.message_id}
        )
        await db.safe_log_action(log_action=action)
        return LikeMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        action = ActionsDbModel(
            action_status=False,
            action_type=ActionsEnum.like_message,
            action_data={"error": f"{ex}"}
        )
        await db.safe_log_action(log_action=action)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )
    finally:
        await account.disconnect()

@router.post(path="/users/enable_2fa", name="users:enable_2fa", tags=["users"],
             description="Enable/disable/change two-factor authentication"
             )
async def enable_2fa(twofa_data: TwoFAModel, user: Union[UserDbModel, None] = Depends(get_user)) -> TwoFAModelResponse:
    account = await TelegramAccount(session_file_name=user.user_session).get_client()
    db = AsyncMongoClient()
    try:
        result = await account.edit_2fa(current_password=twofa_data.current_password, new_password=twofa_data.new_password)
        action = ActionsDbModel(
            action_status=True,
            action_type=ActionsEnum.enable_2fa,
            action_data={"status": result}
        )
        await db.safe_log_action(log_action=action)
        return TwoFAModelResponse(status=StatusEnum.success)
    except Exception as ex:
        action = ActionsDbModel(
            action_status=False,
            action_type=ActionsEnum.enable_2fa,
            action_data={"error": f"{ex}"}
        )
        await db.safe_log_action(log_action=action)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )
    finally:
        await account.disconnect()

@router.get(path="/users/history", name="users:history", tags=["users"],
            description="Get history of operators' messages"
            )
async def get_history(offset: int = 0, limit: int = 10,
                      user: Union[UserDbModel, None] = Depends(get_user)) -> GetHistoryModelResponse:
    db = AsyncMongoClient()
    try:
        result = await db.get_action_history(offset=offset, limit=limit)
        action = ActionsDbModel(
            action_type=ActionsEnum.get_history,
            action_data={"offset": offset, "limit": limit},
            action_status=True
        )
        await db.safe_log_action(log_action=action)
        return GetHistoryModelResponse(status=StatusEnum.success, data=result)
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

@router.get(path="/users/get_dialogs", name="users:dialogs", tags=["users"],
            description="Get full information of session dialogs"
            )
async def get_dialogs(user: Union[UserDbModel, None] = Depends(get_user)):
    account = await TelegramAccount(session_file_name=user.user_session).get_client()
    dialogs_data = str(await account.get_dialogs())
    await account.disconnect()
    return dialogs_data

async def __subscribe_channel(account: TelegramClient, channel: InputChannel, subscribe: bool) -> bool:
    if subscribe:
        await account(JoinChannelRequest(channel))
    else:
        await account(LeaveChannelRequest(channel))
    return True

async def __sent_reaction(account: TelegramClient, message_id: int, peer, emoticon: str) -> bool:
    await account(SendReactionRequest(peer=peer, msg_id=message_id, reaction=[ReactionEmoji(emoticon=emoticon)]))
    return True

def __get_data_from_message_object(message, if_channel: bool, sender_username: str) -> MessageDbModel:
    if if_channel:
        recipient_id = str(message.peer_id.channel_id) if (message.peer_id is not None) else ""
    else:
        recipient_id = str(message.peer_id.user_id) if (message.peer_id is not None) else ""
    return MessageDbModel(
        message_id=message.id,
        message_text=message.message,
        sender_username=sender_username,
        recipient_id=recipient_id
    )