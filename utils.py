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
    }

def parse_user(user:dict) -> User:
    """Parse user dict to user object"""
    return User(id=user["id"], username=user["name"], password=user["password"])