from typing import Any

from fastapi import APIRouter, HTTPException, status
from .api_models import (StatusEnum, SendMessageModel, SendMessageModelResponse,
                        SubscribeChannelModel, SubscribeChannelModelResponse,
                        CommentMessageModel, CommentMessageModelResponse,
                        LikeMessageModel, LikeMessageModelResponse,
                        MessageHistoryModel)

router = APIRouter()


@router.post(path="/send_message", name="users:send_message")
async def send_message(message: SendMessageModel) -> SendMessageModelResponse:
    try:
        return SendMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/subscribe_channel", name="users:subscribe_channel")
async def subscribe_channel(subscribe: SubscribeChannelModel) -> SubscribeChannelModelResponse:
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
async def comment_message(comment: CommentMessageModel) -> CommentMessageModelResponse:
    try:
        return CommentMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/like_message", name="users:like_message")
async def like_message(like: LikeMessageModel) -> LikeMessageModelResponse:
    try:
        return LikeMessageModelResponse(status=StatusEnum.success)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.post(path="/enable_2fa", name="users:enable_2fa")
async def enable_2fa() -> Any:
    try:
        return {"status": "ok"}
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )

@router.get(path="/history", name="users:history")
async def get_history(filters: MessageHistoryModel) -> Any:
    try:
        return {"status": "ok"}
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ex}"
        )
