from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, UUID4

from src.schemas.genres import GenreRead


class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    file_path: str

class BookCreate(BookBase):
    genre_ids: List[UUID4] = []
    author_id: Optional[UUID4] = None

class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    file_path: Optional[str] = None
    genre_ids: Optional[List[UUID4]]


class BookRead(BookBase):
    id: UUID4
    upload_date: datetime
    author_id: UUID4
    rating: float = 0.0
    genres: List[GenreRead] = []

    model_config = {"from_attributes": True}

class BookInDB(BaseModel):
    id: UUID4
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    file_path: str
    upload_date: datetime
    author_id: UUID4
    rating: float

    model_config = {"from_attributes": True}

