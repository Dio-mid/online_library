import uuid

from typing import List
from sqlalchemy import String, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base, uuid_pk


class GenresOrm(Base):
    __tablename__ = "genres"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    books: Mapped[List["BooksOrm"]] = relationship(secondary="book_genre",back_populates="genres", lazy="selectin")


# ---------- Ассоциация Book-Genre (many-to-many) ----------
book_genre = Table(
    "book_genre",
    Base.metadata,
    Column("book_id", PG_UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", PG_UUID(as_uuid=True), ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)