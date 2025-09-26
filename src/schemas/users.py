from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field

from src.dependencies.auth_and_users_dep import RoleEnum


class UserRead(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    is_active: bool
    role: RoleEnum

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = RoleEnum.USER


class UserUpdateSelf(BaseModel):
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6)


class UserUpdateAdmin(BaseModel):
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None
