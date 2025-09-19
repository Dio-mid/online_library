from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[UUID4]
    role_id: Optional[UUID4]
    exp: Optional[datetime]
