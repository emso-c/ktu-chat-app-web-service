from schemas.message import Message
from schemas.user import User


sessions:list[User] = []
all_messages:list[Message] = []
message_queue:list[Message] = []

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