from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):

    email: str
    password: str


class UserLogin(BaseModel):

    email: str
    password: str


class Token(BaseModel):

    access_token: str
    token_type: str

class EmailCreate(BaseModel):

    receiver: str
    subject: str
    body: str


class EmailReply(BaseModel):
    thread_id: int
    receiver: str
    body: str
    subject: str ="RE:"

    