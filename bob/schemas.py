from datetime import datetime
from pydantic import BaseModel


class MessageBase(BaseModel):
    text: str


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    sender: str
    created_at: datetime

    class Config:
        orm_mode = True


class ConversationRead(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        orm_mode = True
