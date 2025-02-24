import datetime
from enum import Enum

from pydantic import BaseModel, Field

class ActionsEnum(str, Enum):
    send_message = "send_message"
    comment_message = "comment_message"
    like_message = "like_message"
    subscribe_channel = "subscribe_channel"
    enable_2fa = "enable_2fa"
    get_history = "get_history"

class UserDbModel(BaseModel):
    username: str = Field(description="user login")
    user_description: str = Field(description="user description")
    user_hashed_password: str = Field(description="user hashed password")
    active: bool = Field(description="active account flag", default=True)

class MessageDbModel(BaseModel):
    message_id: int = Field(description="message id")
    message_text: str = Field(description="message text")
    message_author_id: str = Field(description="author of message")
    created_at: str = Field(description="time of message creation", default=datetime.datetime.now())


class ActionsDbModel(BaseModel):
    action_type: ActionsEnum = Field(description="action type")
    action_status: bool = Field(description="if action was successful")
    action_time: str = Field(description="action time", default=datetime.datetime.now())
