import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Float, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base, uuid_pk


class BooksOrm(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = uuid_pk()
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)

    cover_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("authors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    authors: Mapped[list["AuthorsOrm"]] = relationship(back_populates="books")  # type: ignore[name-defined]

    # Рейтинг хранится и пересчитывается фоново на основе отзывов
    rating: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, server_default=text("0")
    )

    genres: Mapped[list["GenresOrm"]] = relationship(
        secondary="book_genre", back_populates="books"
    )
    reviews: Mapped[list["ReviewsOrm"]] = relationship(
        back_populates="books", cascade="all,delete-orphan", passive_deletes=True
    )
    favourites: Mapped[list["FavouritesOrm"]] = relationship(  # type: ignore[name-defined]
        back_populates="books", cascade="all,delete-orphan", passive_deletes=True
    )