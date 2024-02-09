from datetime import datetime, date
from typing import List, Optional
from pydantic import *


class ContactBase(BaseModel):
    firstname: str = Field(max_length=25)
    lastname: str = Field(max_length=25)
    email: EmailStr = Field(max_length=100)
    phone: int = Field()


class ContactModel(ContactBase):
    birthday: date = Field(None, description="The birthday date Day-Month-Year")


class ContactUpdate(ContactModel):  # updates the whole contact
    done: bool


class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr = Field(max_length=100)
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
