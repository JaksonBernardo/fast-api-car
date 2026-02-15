from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

class UserListPublicSchema(BaseModel):

    users: List[UserPublicSchema]
    offset: int
    limit: int

