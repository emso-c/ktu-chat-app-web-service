from pydantic import BaseModel


class UserBase(BaseModel):
    username:str
    password:str 

    class Config:
        orm_mode = True


class User(UserBase):
    id:int
    last_seen:str=None
    photo_url:str=None
    is_online:bool=False
    is_typing:bool=False
    status:str=None


class UserLogin(UserBase):
    pass


class UserRegister(UserBase):
    firebase_uid:str

class FirebaseUser(BaseModel):
    firebase_uid:str

class UserLogout(BaseModel):
    id:int


class UserMessage(BaseModel):
    id:int
    content:str