import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, DateTime, ForeignKey, Float, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base
from src.utilis.columns import uuid_pk


class BooksOrm(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = uuid_pk()
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    cover_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    author_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("authors.id", ondelete="CASCADE"),
                                                 nullable=False, index=True)
    author: Mapped["AuthorsOrm"] = relationship(back_populates="books") # type: ignore[name-defined]
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default=text("0"))
    genres: Mapped[List["GenresOrm"]] = relationship(secondary="book_genre",back_populates="books",lazy="selectin") # type: ignore[name-defined]
    reviews: Mapped[List["ReviewsOrm"]] = relationship(back_populates="book", cascade="all,delete-orphan", # type: ignore[name-defined]
                                                       passive_deletes=True)
    favourites: Mapped[List["FavouritesOrm"]] = relationship(back_populates="book", cascade="all,delete-orphan", # type: ignore[name-defined]
                                                             passive_deletes=True)
