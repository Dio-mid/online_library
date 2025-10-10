from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    text: str
    rating: int

class ReviewCreate(ReviewBase):
    book_id: UUID

class ReviewUpdate(BaseModel):
    text: Optional[str]
    rating: Optional[int] = Field(None, ge=1, le=5)
    user_id: Optional[UUID] = None

class ReviewRead(ReviewBase):
    user_id: UUID
    book_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}

class ReviewInDB(BaseModel):
    user_id: UUID
    book_id: UUID
    text: str
    rating: int
    created_at: datetime

    model_config = {"from_attributes": True}
