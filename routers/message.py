
from fastapi import APIRouter, Request
from config import PING_INTERVAL, STREAM_DELAY
from db import DBAdapter, DBEngine
import asyncio
from sse_starlette.sse import EventSourceResponse

from schemas.message import Message, MessageSend
from utils import parse_message, parse_user
from session_manager import all_messages, get_recently_received_messages, message_queue

message_router = APIRouter()
db = DBEngine("mobil.db")
adap = DBAdapter(db)

@message_router.post("/send_message/")
async def send_message(message:MessageSend):
    if not message.fromID or not message.toID or not message.content:
        return {"error": "Message sending failed"}

    message = Message(fromID=message.fromID, toID=message.toID, content=message.content)
    try:
        db.add_message(message.fromID, message.toID, message.content)
    except Exception as e:
        return {"error": "Message sending failed"}

    all_messages.append(message)
    message_queue.append(message)
    return {"message": "Message sent"}

@message_router.get("/all-messages/")
async def messages_view():
    return adap.get_messages()

@message_router.get("/received-messages/")
async def received_messages_view(_id:int):
    messages = adap.get_all_received_messages(_id)
    return messages

async def event_generator(request: Request, user_id:int):
    while True:
        if await request.is_disconnected():
            break

        user = adap.get_user(user_id)
        user = parse_user(user)
        for message in get_recently_received_messages(user):
            yield {
                "id": 0,
                "event": "message",
                "data": parse_message(message),
                "retry": 0
            }
            message_queue.remove(message)
        await asyncio.sleep(STREAM_DELAY)

@message_router.get('/message-stream')
async def message_stream(request: Request, _id:int):
    event_source = EventSourceResponse(event_generator(request, _id))
    event_source.ping_interval = PING_INTERVAL
    return event_source
