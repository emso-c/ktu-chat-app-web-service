from datetime import datetime
from schemas.message import Message
from schemas.user import User


def parse_message(message:Message) -> Message:
    """Parse message to json with string values"""
    return {
        "id": str(message.id),
        "fromID": str(message.fromID),
        "toID": str(message.toID),
        "content": message.content,
        "date": str(message.date),
        "seen": str(message.seen),
    }

def parse_user(user:dict) -> User:
    """Parse user dict to user object"""
    return User(
        id=user["id"],
        username=user["name"],
        password=user["password"],
        # don't need to parse firebase_uid as it's only used for syncing
        last_seen=user["last_seen"],
        photo_url=user["photo_url"],
        is_online=user["is_online"],
        is_typing=user["is_typing"],
        status=user["status"]
    )

def sort_dates(messages: list[dict]) -> list[dict]:
    for message in messages:
        message['date'] = datetime.strptime(message['date'], "%d-%m-%Y %H:%M:%S")
    
    messages.sort(key=lambda x: x['date'])
    
    for message in messages:
        message['date'] = message['date'].strftime("%d-%m-%Y %H:%M:%S")
