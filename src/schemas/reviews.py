from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    text: str
    rating: float

class ReviewCreate(ReviewBase):
    book_id: UUID

class ReviewUpdate(BaseModel):
    text: Optional[str]
    rating: Optional[float] = Field(None, ge=1, le=5)

class ReviewRead(ReviewBase):
    id: UUID
    user_id: UUID
    book_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
