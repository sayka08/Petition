from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    username: str
    password: str

class PetitionBase(BaseModel):
    title: str
    description: str

class PetitionCreate(PetitionBase):
    pass

class PetitionResponse(PetitionBase):
    id: int
    votes_count: int
    created_at: datetime

    class Config:
        orm_mode = True

class VoteCreate(BaseModel):
    petition_id: int

class VoteResponse(BaseModel):
    id: int
    user_id: int
    petition_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TokenRequest(BaseModel):
    token: str
