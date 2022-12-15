import asyncio
import uvicorn
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from datetime import datetime
import socket
from pydantic import BaseModel, Field

class User(BaseModel):
    id:int = None
    username:str = None

class Message(BaseModel):
    id:int = None
    fromID:int = None
    toID:int = None
    content:str = None
    date:datetime = Field(default_factory=datetime.now)

def parse_message(message:Message) -> Message:
    """Parse message to json with string values"""
    return {
        "id": str(message.id),
        "fromID": str(message.fromID),
        "toID": str(message.toID),
        "content": message.content,
        "date": str(message.date),
    }

def get_all_received_messages():
    # Message control logic here
    for message in all_messages:
        if message.toID == session.id:
            yield message
    return None

def get_recently_received_messages():
    # Message control logic here
    for message in message_queue:
        if message.toID == session.id:
            yield message
    return None

STREAM_DELAY = 3  # second
PING_INTERVAL = 30  # second

all_messages:list[Message] = []
message_queue:list[Message] = []
session:User = User(
    id=1,
    username="test",
)
app = FastAPI()

@app.get("/")
async def root():
    message = Message(
        fromID=1,
        toID=1,
        content="hello",
    )
    return {"message": "Hello World", "msg": message}

@app.get("/login/")
async def login():
    global session
    session.username = "emir"
    return {"message": "Login successful", "username": session.username}

@app.get("/message/")
async def send_message(toID:int=None, content:str=None):
    # TODO: validate & convert to post request
    message = Message(
        id=len(all_messages) + 1,
        fromID = session.id,
        toID = toID,
        content = content,
    )
    message_queue.append(message)
    all_messages.append(message)
    return {"status": "success", "message": message, "total message amount": len(all_messages)}

@app.get("/all_messages/")
async def all_messages_view():
    return [parse_message(message) for message in get_all_received_messages()]

async def event_generator(request: Request):
    while True:
        if await request.is_disconnected():
            break

        for i, message in enumerate(get_recently_received_messages()):
            yield {
                "id": 0, # len(all_messages) + 1,
                "event": "message",
                "data": parse_message(message),
                "retry": 0
            }
            message_queue.remove(message)
        await asyncio.sleep(STREAM_DELAY)

@app.get('/message-stream')
async def message_stream(request: Request):
    event_source = EventSourceResponse(event_generator(request))
    event_source.ping_interval = PING_INTERVAL
    return event_source


if __name__ == "__main__":
    hostname=socket.gethostname()
    ip_address=socket.gethostbyname(hostname)
    print(f"Host Computer: {hostname} - {ip_address}")

    # run from terminal: uvicorn main:app --host 0.0.0.0 --port 8000 --reload 
    uvicorn.run("my_app.main:app", host=ip_address, port=8002, reload=True)
    uvicorn.run("sql_app.main:app", host=ip_address, port=8001, reload=True)
    #uvicorn.run("__main__:app", host=ip_address, port=8000, reload=True)
