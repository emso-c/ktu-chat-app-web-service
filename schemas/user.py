from pydantic import BaseModel


class UserBase(BaseModel):
    username:str
    password:str 

    class Config:
        orm_mode = True


class User(UserBase):
    id:int


class UserLogin(UserBase):
    pass


class UserRegister(UserBase):
    pass


class UserLogout(BaseModel):
    id:int


class UserMessage(BaseModel):
    id:int
    content:str