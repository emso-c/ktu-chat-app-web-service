from db import DBAdapter, DBEngine
from schemas.message import Message
from schemas.user import User

_db = DBEngine("mobil.db")
_adap = DBAdapter(_db)

sessions:list[User] = []
all_messages:list[Message] = []
message_queue:list[Message] = []

def get_current_session(user:User) -> User:
    for user_session in sessions:
        if user_session.id == user.id:
            return user_session
    return None

def add_session(user:User):
    sessions.append(user)

def remove_session(user:User):
    for user_session in sessions:
        if user_session.id == user.id:
            sessions.remove(user_session)
            return True
    return False

def get_received_messages(user:User, messages:list[Message]):
    # TODO: Temporarily disable sessions
    # user_session = get_current_session(user)
    # if not user_session:
    #     return None
    for message in messages:
        if message.toID == user.id: # TODO change user to user_session.id
            yield message
    return None

def get_all_received_messages(user:User):
    all_messages = _adap.get_all_received_messages(user.id)
    return get_received_messages(user, all_messages)

def get_recently_received_messages(user:User):
    return get_received_messages(user, message_queue)