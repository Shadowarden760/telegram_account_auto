from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StatusEnum(str, Enum):
    success = "success"
    failure = "failure"

class SendMessageModel(BaseModel):
    chat_id: int = Field(description="chat id for sending message")
    message: str = Field(description="message for sending")
    media: Optional[str] = Field(description="url path to media for sending")

class SendMessageModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    message_id: Optional[str] = Field(description="new message id", default=0)
    error_text: Optional[str] = Field(description="error description", default="")

class SubscribeChannelModel(BaseModel):
    channel_name: Optional[str] = Field(description="channel name")
    channel_id: Optional[str] = Field(description="channel id")

class SubscribeChannelModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    channel_id: str = Field(description="channel id", default="")
    channel_name: str = Field(description="channel name", default="")
    error_text: Optional[str] = Field(description="error description", default="")

class CommentMessageModel(BaseModel):
    channel_id: str = Field(description="channel id to comment")
    message_id: int = Field(description="message id to comment")
    comment: str = Field(description="text comment to message")

class CommentMessageModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    error_text: Optional[str] = Field(description="error description", default="")

class LikeMessageModel(BaseModel):
    channel_id: str = Field(description="channel id to like")
    message_id: int = Field(description="message id to like")

class LikeMessageModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    error_text: Optional[str] = Field(description="error description", default="")

class MessageHistoryModel(BaseModel):
    limit: int = Field(description="message limit", default=10)
    offset: Optional[int] = Field(description="count of last messages to ignore")