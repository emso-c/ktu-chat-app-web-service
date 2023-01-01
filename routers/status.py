
from db import DBAdapter, DBEngine
from schemas.user import UserLogin, UserLogout, UserRegister, FirebaseUser, UserUpdate
from fastapi import APIRouter
from session_manager import sessions
from utils import parse_user

status_router = APIRouter()
db = DBEngine("mobil.db")
adap = DBAdapter(db)

@status_router.get("/add-status/")
async def add_status(_id:int, image_url:str):
    if not _id or not image_url:
        return {"error": "Invalid parameters"}
    db.add_status(_id, image_url)
    return {"message": "Status added"}

@status_router.get("/statuses/")
async def get_statuses():
    return adap.get_statuses()

@status_router.get("/get-status/")
async def get_status(_id:int):
    if not _id:
        return {"error": "Invalid parameters"}
    status = adap.get_status(_id)
    if not status:
        return {"error": "Status not found"}
    return status

@status_router.get("/delete-status/")
async def delete_status(_id:int):
    if not _id:
        return {"error": "Invalid parameters"}
    db.delete_status(_id)
    return {"message": "Status deleted"}



