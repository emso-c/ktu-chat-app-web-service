from datetime import datetime
import sqlite3

class DBEngine:
    def __init__(self, db_name):
        self.con = sqlite3.connect(db_name)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, password TEXT, firebase_uid TEXT, last_seen TEXT, photo_url TEXT, is_online BOOLEAN, is_typing BOOLEAN, status TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, fromID INTEGER, toID INTEGER, content TEXT, date TEXT, seen BOOLEAN DEFAULT 0)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS statuses (id INTEGER PRIMARY KEY, user_id INTEGER, image_url TEXT, date TEXT)")
        self.con.commit()

    def __del__(self):
        self.con.close()
    
    def info(self):
        return self.cur.execute("SELECT * FROM sqlite_master WHERE type='table'").fetchall()

    def add_user(self, name:str, password:str, firebase_uid:str, date:str="", photo_url:str="", ) -> int:
        if not date:
            date = date or datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.cur.execute(
            "INSERT INTO users (name, password, firebase_uid, last_seen, photo_url, is_online, is_typing, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, password, firebase_uid, date, photo_url, False, False, ""))
        self.con.commit()
        return self.cur.lastrowid

    def get_user(self, user_id:int) -> tuple:
        return self.cur.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    
    def get_user_by_name(self, name:str) -> tuple:
        return self.cur.execute("SELECT * FROM users WHERE name=?", (name,)).fetchone()

    def get_user_by_firebase_uid(self, firebase_uid:str) -> tuple:
        return self.cur.execute("SELECT * FROM users WHERE firebase_uid=?", (firebase_uid,)).fetchone()
    
    def get_users(self) -> list:
        return self.cur.execute("SELECT * FROM users").fetchall()
    
    def delete_user(self, user_id:int):
        self.cur.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.con.commit()
    
    def update_user(self, user_id:int, name:str, password:str, firebase_uid:str, date:str, photo_url:str="", is_online:bool=False, is_typing:bool=False, status:str=""):
        if not date:
            date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.cur.execute("UPDATE users SET name=?, password=?, firebase_uid=?, last_seen=?, photo_url=?, is_online=?, is_typing=?, status=? WHERE id=?",(name, password, firebase_uid, date, photo_url, is_online, is_typing, status, user_id))
        self.con.commit()

    def add_message(self, fromID:int, toID:int, content:str, date:str=None) -> int:
        if not self.get_user(fromID):
            raise Exception("User with id {} does not exist".format(fromID))
        if not self.get_user(toID):
            raise Exception("User with id {} does not exist".format(toID))
        if not date:
            date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.cur.execute("INSERT INTO messages VALUES (null, ?, ?, ?, ?, ?)", (fromID, toID, content, date, False))
        self.con.commit()
        return self.cur.lastrowid
    
    def get_message(self, message_id:int) -> tuple:
        return self.cur.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()
    
    def get_messages(self) -> list:
        return self.cur.execute("SELECT * FROM messages").fetchall()
    
    def get_messages_by_user(self, user_id:int) -> list:
        return self.cur.execute("SELECT * FROM messages WHERE fromID=? OR toID=?", (user_id, user_id)).fetchall()
    
    def delete_message(self, message_id:int):
        result = self.cur.execute("DELETE FROM messages WHERE id=?", (message_id,))
        self.con.commit()
        return result
    
    def update_message(self, message_id:int, fromID:int, toID:int, content:str, date:str):
        if not self.get_user(fromID):
            raise Exception("User with id {} does not exist".format(fromID))
        if not self.get_user(toID):
            raise Exception("User with id {} does not exist".format(toID))
        if not date:
            date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.cur.execute("UPDATE messages SET fromID=?, toID=?, content=?, date=? WHERE id=?", (fromID, toID, content, date, message_id))
        self.con.commit()
    
    def get_all_received_messages(self, user_id:int) -> list:
        return self.cur.execute("SELECT * FROM messages WHERE toID=?", (user_id,)).fetchall()
    
    def get_all_sent_messages(self, user_id:int) -> list:
        return self.cur.execute("SELECT * FROM messages WHERE fromID=?", (user_id,)).fetchall()
    
    def clear_all_messages(self):
        self.cur.execute("DELETE FROM messages")
        self.con.commit()
    
    def clear_all_users(self):
        self.cur.execute("DELETE FROM users")
        self.con.commit()
    
    def clear_all(self):
        self.clear_all_messages()
        self.clear_all_users()
    
    def user_exists(self, user_id:int) -> bool:
        return self.get_user(user_id) is not None
    
    def get_user_by_username(self, username:str) -> tuple:
        return self.cur.execute("SELECT * FROM users WHERE name=?", (username,)).fetchone()
    
    def get_user_by_username_and_password(self, username:str, password:str) -> tuple:
        return self.cur.execute("SELECT * FROM users WHERE name=? AND password=?", (username, password)).fetchone()
    
    def update_user_last_seen(self, user_id:int, date:str=None):
        if not date:
            date = date or datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        # update and return the updated user
        self.cur.execute("UPDATE users SET last_seen=? WHERE id=?", (date, user_id))
        self.con.commit()
        return self.get_user(user_id)

    def update_user_is_online(self, user_id:int, is_online:bool):
        self.cur.execute("UPDATE users SET is_online=? WHERE id=?", (is_online, user_id))
        self.con.commit()
        return self.get_user(user_id)
    
    def update_user_is_typing(self, user_id:int, is_typing:bool):
        self.cur.execute("UPDATE users SET is_typing=? WHERE id=?", (is_typing, user_id))
        self.con.commit()
        return self.get_user(user_id)
    
    def update_user_status(self, user_id:int, status:str):
        self.cur.execute("UPDATE users SET status=? WHERE id=?", (status, user_id))
        self.con.commit()
        return self.get_user(user_id)
    
    def update_user_photo_url(self, user_id:int, photo_url:str):
        self.cur.execute("UPDATE users SET photo_url=? WHERE id=?", (photo_url, user_id))
        self.con.commit()
        return self.get_user(user_id)
    
    def update_user_name(self, user_id:int, name:str):
        self.cur.execute("UPDATE users SET name=? WHERE id=?", (name, user_id))
        self.con.commit()
        return self.get_user(user_id)
    
    def update_user_password(self, user_id:int, password:str):
        self.cur.execute("UPDATE users SET password=? WHERE id=?", (password, user_id))
        self.con.commit()
        return self.get_user(user_id)
    
    def set_message_seen(self, message_id:int, seen:bool):
        self.cur.execute("UPDATE messages SET seen=? WHERE id=?", (seen, message_id))
        self.con.commit()
        return self.get_message(message_id)
    

    def get_statuses(self) -> list:
        return self.cur.execute("SELECT * FROM statuses").fetchall()
    
    def get_status(self, status_id:int) -> tuple:
        return self.cur.execute("SELECT * FROM statuses WHERE id=?", (status_id,)).fetchone()
    
    def add_status(self, user_id:int, image_url:str, date:str=None):
        if not date:
            date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.cur.execute("INSERT INTO statuses VALUES (null, ?, ?, ?)", (user_id, image_url, date))
        self.con.commit()
        return self.get_status(self.cur.lastrowid)
    
    def delete_status(self, status_id:int):
        self.cur.execute("DELETE FROM statuses WHERE id=?", (status_id,))
        self.con.commit()    


class DBAdapter:
    """A class to convert database responses to JSON format"""
    def __init__(self, db:DBEngine):
        self.db = db
    
    def get_user(self, user_id:int) -> dict:
        user = self.db.get_user(user_id)
        if not user:
            return None
        return _user_to_dict(user)
    
    def get_users(self) -> list:
        users = self.db.get_users()
        return [_user_to_dict(user) for user in users]
    
    def get_message(self, message_id:int) -> dict:
        message = self.db.get_message(message_id)
        if not message:
            return None
        return _message_to_dict(message)
    
    def get_messages(self) -> list:
        messages = self.db.get_messages()
        return [_message_to_dict(message) for message in messages]
    
    def get_messages_by_user(self, user_id:int) -> list:
        messages = self.db.get_messages_by_user(user_id)
        return [_message_to_dict(message) for message in messages]
    
    def get_all_received_messages(self, user_id:int) -> list:
        messages = self.db.get_all_received_messages(user_id)
        return [_message_to_dict(message) for message in messages]
    
    def get_all_sent_messages(self, user_id:int) -> list:
        messages = self.db.get_all_sent_messages(user_id)
        return [_message_to_dict(message) for message in messages]
    
    def clear_all(self):
        self.db.clear_all()
    
    def user_exists(self, user_id:int) -> bool:
        return self.db.user_exists(user_id)
    
    def get_user_by_username(self, username:str) -> dict:
        user = self.db.get_user_by_username(username)
        if not user:
            return None
        return _user_to_dict(user)
    
    def get_user_by_username_and_password(self, username:str, password:str) -> dict:
        user = self.db.get_user_by_username_and_password(username, password)
        if not user:
            return None
        return _user_to_dict(user)
    
    def get_user_by_firebase_uid(self, firebase_uid:str) -> dict:
        user = self.db.get_user_by_firebase_uid(firebase_uid)
        if not user:
            return None
        return _user_to_dict(user)
    
    def get_status(self, status_id:int) -> dict:
        status = self.db.get_status(status_id)
        if not status:
            return None
        return _status_to_dict(status)
    
    def get_statuses(self) -> list:
        statuses = self.db.get_statuses()
        return [_status_to_dict(status) for status in statuses]

def _user_to_dict(user:list) -> dict:
    return {
        "id": user[0],
        "name": user[1],
        "password": user[2],
        "firebase_uid": user[3],
        "last_seen": user[4],
        "photo_url": user[5],
        "is_online": user[6],
        "is_typing": user[7],
        "status": user[8]
    }

def _message_to_dict(message:list) -> dict:
    return {
        "id": message[0],
        "fromID": message[1],
        "toID": message[2],
        "content": message[3],
        "date": message[4],
        "seen": message[5]
    }

def _status_to_dict(status:list) -> dict:
    return {
        "id": status[0],
        "user_id": status[1],
        "image_url": status[2],
        "date": status[3]
    }

""" USAGE EXAMPLE 
db = DBEngine("mobil.db")

db.add_user("Ahmet", "1234")
db.add_user("Mehmet", "1234")

db.add_message(1, 2, "Hello")
db.add_message(2, 1, "Hi")

adapter = DBAdapter(db)
print(adapter.get_users())
print(adapter.get_messages())

db.clear_all()

 """