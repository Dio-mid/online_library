from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4

from src.utilis.enums import RoleEnum


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID4]
    role: Optional[RoleEnum]
    exp: Optional[datetime]
