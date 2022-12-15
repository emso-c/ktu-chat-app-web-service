import asyncio
import uvicorn
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from datetime import datetime
import socket
from pydantic import BaseModel, Field

from db import DBEngine, DBAdapter


class UserBase(BaseModel):
    username:str
    password:str 

    class Config:
        orm_mode = True
class User(UserBase):
    id:int

class UserLogin(UserBase):
    pass

class UserRegister(UserBase):
    pass

class UserLogout(BaseModel):
    id:int

class Message(BaseModel):
    id:int = None
    fromID:int = None
    toID:int = None
    content:str = None
    date:datetime = Field(default_factory=datetime.now)

STREAM_DELAY = 3  # second
PING_INTERVAL = 30  # second

all_messages:list[Message] = []
message_queue:list[Message] = []
sessions:list[User] = []

app = FastAPI()
db = DBEngine("mobil.db")
adap = DBAdapter(db)

def parse_message(message:Message) -> Message:
    """Parse message to json with string values"""
    return {
        "id": str(message.id),
        "fromID": str(message.fromID),
        "toID": str(message.toID),
        "content": message.content,
        "date": str(message.date),
    }

def parse_user(user:dict) -> User:
    """Parse user dict to user object"""
    return User(id=user["id"], username=user["name"], password=user["password"])

def get_current_session(user:User) -> User:
    for session in sessions:
        if session.id == user.id:
            return session
    return None

def add_session(user:User):
    sessions.append(user)

def remove_session(user:User):
    for session in sessions:
        if session.id == user.id:
            sessions.remove(session)
            return True
    return False

def get_received_messages(user:User, messages:list[Message]):
    session = get_current_session(user)
    if not session:
        return None
    for message in messages:
        if message.toID == session.id:
            yield message
    return None

def get_all_received_messages(user:User):
    return get_received_messages(user, all_messages)

def get_recently_received_messages(user:User):
    return get_received_messages(user, message_queue)

@app.get("/")
async def root():
    return {"message": "Hello World", "msg": "Welcome to Chat App"}

@app.post("/register/")
async def register(user:UserRegister):
    if not user.username or not user.password:
        return {"error": "Registration failed"}
    if adap.get_user_by_username(user.username):
        return {"error": "User already exists"}
    db.add_user(user.username, user.password)
    return {"message": "Registration successful"}

@app.post("/login/")
async def login(user:UserLogin):
    if not user.username or not user.password:
        return {"error": "Login failed"}

    found_user = adap.get_user_by_username_and_password(user.username, user.password)
    if not found_user:
        return {"error": "Login failed"}

    user = parse_user(found_user)
    if user not in sessions:
        sessions.append(user)
    
    return {"message": "Login successful", "username": user.username, "id": user.id}

@app.post("/logout/")
async def logout(user:UserLogout):
    if not user.id:
        return {"message": "Logout failed"}
    
    found_user = adap.get_user(user.id)
    if not found_user:
        return {"message": "Logout failed"}

    user = parse_user(found_user)
    if user in sessions:
        sessions.remove(user)
    return {"message": "Logout successful"}

@app.get("/users/")
async def users_view():
    return adap.get_users()

@app.get("/sessions/")
async def sessions_view():
    return sessions


@app.post("/message/")
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
    uvicorn.run("__main__:app", host=ip_address, port=8000, reload=True)
