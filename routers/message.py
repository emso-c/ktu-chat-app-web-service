
from fastapi import APIRouter, Request
from config import PING_INTERVAL, STREAM_DELAY
from db import DBAdapter, DBEngine
import asyncio
from sse_starlette.sse import EventSourceResponse

from schemas.message import Message, MessageSend
from utils import parse_message, parse_user, sort_dates
from session_manager import all_messages, get_recently_received_messages, message_queue

message_router = APIRouter()
db = DBEngine("mobil.db")
adap = DBAdapter(db)

@message_router.post("/send-message/")
async def send_message(message:MessageSend):
    if not message.fromID or not message.toID or not message.content:
        return {"error": "Invalid parameters"}

    message = Message(fromID=message.fromID, toID=message.toID, content=message.content)
    last_inserted_id = None
    try:
        last_inserted_id = db.add_message(message.fromID, message.toID, message.content)
    except Exception as e:
        return {"error": "Message sending failed", "exception": e.__str__()}

    all_messages.append(message)
    message_queue.append(message)
    return {"id": last_inserted_id}

@message_router.get("/all-messages/")
async def messages_view():
    return adap.get_messages()

@message_router.get("/received-messages/")
async def received_messages_view(_id:int):
    messages = adap.get_all_received_messages(_id)
    return messages

@message_router.get("/chat-history/")
async def chat_history(_id:int):
    received_messages:list[dict] = adap.get_all_received_messages(_id)
    sent_messages:list[dict] = adap.get_all_sent_messages(_id)
    messages = received_messages + sent_messages
    sort_dates(messages)
    users = {}
    for message in messages:
        if message["fromID"] is _id:
            if message["toID"] not in users:
                user = adap.get_user(message["toID"])
                users[message["toID"]] = {
                    "messages": [],
                    "username": user["name"],
                    "firebase_uid": user["firebase_uid"],
                    "last_message": None,
                    "last_message_date": None,
                    "last_seen": user["last_seen"],
                    "unseen_messages": 0,
                }
            users[message["toID"]]["messages"].append(message)
            users[message["toID"]]["last_message"] = message["content"]
            users[message["toID"]]["last_message_date"] = message["date"]
        else:
            last_message:str = "✔✔ "
            if message["fromID"] not in users:
                user = adap.get_user(message["fromID"])
                users[message["fromID"]] = {
                    "messages": [],
                    "username": user["name"],
                    "firebase_uid": user["firebase_uid"],
                    "last_message": None,
                    "last_message_date": None,
                    "last_seen": user["last_seen"],
                    "unseen_messages": 0,
                }
            else:
                if message["seen"] == 0:
                    users[message["fromID"]]["unseen_messages"] += 1
                    last_message = "✔ "
            users[message["fromID"]]["messages"].append(message)
            users[message["fromID"]]["last_message"] = last_message + message["content"]
            users[message["fromID"]]["last_message_date"] = message["date"]
    return users

@message_router.get("/chat-history-with-user/")
async def get_chat_history_with_user(_id:int, _target_id:int):
    received_messages:list[dict] = adap.get_all_received_messages(_id)
    sent_messages:list[dict] = adap.get_all_sent_messages(_id)
    messages = received_messages + sent_messages
    sort_dates(messages)

    user = adap.get_user(_target_id)
    user = {
        "messages": [],
        "username": user["name"],
        "user_id": user["id"],
        "firebase_uid": user["firebase_uid"],
        "last_message": None,
        "last_message_date": None,
        "last_seen": user["last_seen"],
        "unseen_messages": 0,
    }

    for message in messages:
        if message["fromID"] == _target_id or message["toID"] == _target_id:
            user["messages"].append(message)
            user["last_message"] = message["content"]
            user["last_message_date"] = message["date"]
            if message["fromID"] != _id and message["seen"] == 0:
                user["unseen_messages"] += 1
    return user

newly_seen_messages_exists = False
@message_router.get("/set-message-seen/")
async def set_message_seen(_id:int):
    db.set_message_seen(_id, True)
    global newly_seen_messages_exists
    newly_seen_messages_exists = True
    return {"status": "success"}

@message_router.delete("/delete-message/")
async def delete_message(_id:int):
    db.delete_message(_id)
    return {"status": "success"}

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
        global newly_seen_messages_exists
        if newly_seen_messages_exists:
            yield {
                "id": 0,
                "event": "seen",
                "data": "seen",
                "retry": 0
            }
            newly_seen_messages_exists = False
        await asyncio.sleep(STREAM_DELAY)

@message_router.get('/message-stream')
async def message_stream(request: Request, _id:int):
    event_source = EventSourceResponse(event_generator(request, _id))
    event_source.ping_interval = PING_INTERVAL
    return event_source
