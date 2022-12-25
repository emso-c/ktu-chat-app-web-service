from datetime import datetime
from pydantic import BaseModel, Field

class Message(BaseModel):
    id:int = None
    fromID:int = None
    toID:int = None
    content:str = None
    date:datetime = Field(default_factory=datetime.now)

class MessageSend(BaseModel):
    fromID:int
    toID:int
    content:str