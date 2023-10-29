from pydantic import BaseModel
from datetime import datetime
from pydantic.networks import EmailStr
from typing import Optional




class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number:Optional[str] = None
    password: str

class ResetPassword(BaseModel):
    email:EmailStr

class UpdateUserData(BaseModel):
    first_name: str
    last_name: str
    phone_number:Optional[str] = None
    password: str


class LoginUser(BaseModel):
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None

