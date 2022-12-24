from datetime import datetime
from pydantic import BaseModel, Field

class Message(BaseModel):
    id:int = None
    fromID:int = None
    toID:int = None
    content:str = None
    date:datetime = Field(default_factory=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

class MessageSend(BaseModel):
    fromID:int
    toID:int
    content:str