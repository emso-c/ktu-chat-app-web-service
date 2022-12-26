
from db import DBAdapter, DBEngine
from schemas.user import UserLogin, UserLogout, UserRegister, FirebaseUser
from fastapi import APIRouter
from session_manager import sessions
from utils import parse_user

user_router = APIRouter()
db = DBEngine("mobil.db")
adap = DBAdapter(db)

@user_router.post("/get-user-by-firebase-uid/")
async def get_user_by_firebase_uid(fb_user:FirebaseUser):
    if not fb_user.firebase_uid:
        return {"error": "Invalid Firebase UID"}
    user = adap.get_user_by_firebase_uid(fb_user.firebase_uid)
    if not user:
        return {"error": "User not found"}
    return user

@user_router.get("/get-user-by-id/")
async def get_user_by_id(_id:int):
    # TODO security issue do not return password 
    if not _id:
        return {"error": "Invalid id"}
    user = adap.get_user(_id)
    if not user:
        return {"error": "User not found"}
    return user

@user_router.get("/get-user-by-username/")
async def get_user_by_username(username:str):
    # TODO security issue do not return password 
    if not username:
        return {"error": "Invalid username"}
    user = adap.get_user_by_username(username)
    if not user:
        return {"error": "User not found"}
    return user

@user_router.post("/register/")
async def register(user:UserRegister):
    if not user.username or not user.password or not user.firebase_uid:
        return {"error": "Invalid parameters"}
    if adap.get_user_by_username(user.username):
        return {"error": "User already exists"}
    db.add_user(user.username, user.password, user.firebase_uid)
    return {"message": "Registration successful"}

@user_router.delete("/delete-user/")
async def delete_user(user:UserLogout):
    if not user.id:
        return {"message": "Invalid id"}
    
    found_user = adap.get_user(user.id)
    if not found_user:
        return {"message": "User not found"}

    user = parse_user(found_user)
    if user in sessions:
        sessions.remove(user)
    db.delete_user(user.id)
    return {"message": "Delete successful"}

@user_router.get("/users/")
async def users_view():
    return adap.get_users()

@user_router.post("/login/")
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

@user_router.post("/logout/")
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

@user_router.get("/sessions/")
async def sessions_view():
    return sessions