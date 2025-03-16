import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ActionsEnum(str, Enum):
    login = "login"
    send_message = "send_message"
    comment_message = "comment_message"
    like_message = "like_message"
    subscribe_channel = "subscribe_channel"
    enable_2fa = "enable_2fa"
    get_history = "get_history"
    
    
class UserRoles(str, Enum):
    admin = "admin"
    operator = "operator"


class UserDbModel(BaseModel):
    username: str = Field(description="user login")
    user_hashed_password: str = Field(description="user hashed password")
    user_description: str = Field(description="user description", default="default user")
    user_role: UserRoles = Field(description="user role", default=UserRoles.operator) 
    active: bool = Field(description="active account flag", default=True)


class MessageDbModel(BaseModel):
    message_id: int = Field(description="message id")
    message_text: str = Field(description="message text")
    sender_id: str = Field(description="author of message")
    recipient_id: str = Field(description="recipient of message")
    created_at: datetime.datetime = Field(description="time of message creation", default=datetime.datetime.now())


class ActionsDbModel(BaseModel):
    action_type: ActionsEnum = Field(description="action type")
    action_data: dict = Field(description="action data")
    action_status: bool = Field(description="if action was successful")
    action_time: datetime.datetime = Field(description="action time", default=datetime.datetime.now())
