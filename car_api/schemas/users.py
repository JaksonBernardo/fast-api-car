from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import datetime

class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    def username_min_length(cls, v):

        if len(v) < 3:

            raise ValueError("Username deve ter pelo menos 6 caracteres")
        
        return v
    
    @field_validator("password")
    def password_min_length(cls, v):

        if len(v) < 6:

            raise ValueError("Password deve ter pelo menos 6 caracteres")
        
        return v

class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("username")
    def username_min_length(cls, v):

        if len(v.strip()) < 3:

            raise ValueError("Username deve ter pelo menos 6 caracteres")
        
        return v
    
    @field_validator("password")
    def password_min_length(cls, v):

        if len(v.strip()) < 6:

            raise ValueError("Password deve ter pelo menos 6 caracteres")
        
        return v


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

class UserListPublicSchema(BaseModel):

    users: List[UserPublicSchema]
    offset: int
    limit: int

