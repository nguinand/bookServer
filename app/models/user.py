from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserModel(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password_hash: str
    role: str = "user"
    avatar_id: Optional[int] = None
    status_id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
