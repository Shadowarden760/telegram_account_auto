import json
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator

from database.models import UserRoles, MessageDbModel


class StatusEnum(str, Enum):
    success = "success"
    failure = "failure"

class SendMessageModel(BaseModel):
    chat_id: int = Field(description="chat id for sending message", default=0)
    text_message: str = Field(description="message for sending", default="")
    if_channel: bool = Field(description="channel or not", default=False)

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class SendMessageModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    message_id: Optional[List[int]] = Field(description="new messages ids", default=[])

class SubscribeChannelModel(BaseModel):
    channel_name: Optional[str] = Field(description="channel name", default=None)
    channel_id: Optional[int] = Field(description="channel id", default=None)
    subscribe_flag: bool = Field(description="subscribe or not")

class SubscribeChannelModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    channel_id: str = Field(description="channel id", default="")
    channel_name: str = Field(description="channel name", default="")

class CommentMessageModel(BaseModel):
    channel_id: int = Field(description="channel id to comment")
    message_id: int = Field(description="message id to comment")
    comment: str = Field(description="text comment to message")

class CommentMessageModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    error_text: Optional[str] = Field(description="error description", default="")

class LikeMessageModel(BaseModel):
    chat_id: int = Field(description="chat id to like")
    message_id: int = Field(description="message id to like")
    if_channel: bool = Field(description="channel or not", default=False)

class LikeMessageModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    error_text: Optional[str] = Field(description="error description", default="")

class TwoFAModel(BaseModel):
    current_password: Optional[str] = Field(description="current password, ignore if 2fa not activated", default=None)
    new_password: Optional[str] = Field(description="new password, ignore to reset 2fa", default=None)

class TwoFAModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")

class GetHistoryModelResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    data: List[MessageDbModel] = Field(description="history of messaging", default=[])

class AdminInsertUserModel(BaseModel):
    new_username: str = Field(description="new username")
    new_user_password: str = Field(description="new password")
    new_user_description: str = Field(description="new description", default="default operator")
    new_user_role: UserRoles = Field(description="new user role", default=UserRoles.operator)
    new_user_active: bool = Field(description="if user active or disabled", default=True)

class AdminUpdateUserModel(BaseModel):
    updated_username: Optional[str] = Field(description="updated username", default=None)
    updated_user_password: Optional[str] = Field(description="updated password", default=None)
    updated_user_description: Optional[str] = Field(description="updated description", default=None)
    updated_user_role: Optional[UserRoles] = Field(description="updated user role", default=None)
    updated_user_active: Optional[bool] = Field(description="if user active or disabled", default=None)

class AdminActionResponse(BaseModel):
    status: StatusEnum = Field(description="operation status")
    data: dict = Field(description="operation result data", default={})
