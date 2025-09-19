from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field

class UserRead(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    is_active: bool
    role_id: Optional[UUID4]

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: Optional[UUID4]

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role_id: Optional[UUID4] = None
    is_active: Optional[bool] = None
