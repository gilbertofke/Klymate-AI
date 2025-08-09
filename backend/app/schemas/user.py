from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    location: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    firebase_uid: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
