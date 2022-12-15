
from db import DBAdapter, DBEngine
from schemas.user import UserLogin, UserLogout, UserRegister
from fastapi import APIRouter
from session_manager import sessions
from utils import parse_user

user_router = APIRouter()
db = DBEngine("mobil.db")
adap = DBAdapter(db)

@user_router.post("/register/")
async def register(user:UserRegister):
    if not user.username or not user.password:
        return {"error": "Registration failed"}
    if adap.get_user_by_username(user.username):
        return {"error": "User already exists"}
    db.add_user(user.username, user.password)
    return {"message": "Registration successful"}

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