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
    genre_ids: List[UUID4] = []  # список UUID жанров

class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    file_path: Optional[str] = None
    genre_ids: Optional[List[UUID4]]  # если передан, обновляем связи


class BookRead(BookBase):
    id: UUID4
    upload_date: datetime
    author_id: UUID4
    rating: float
    genres: List[GenreRead] = []

    class Config:
        orm_mode = True

