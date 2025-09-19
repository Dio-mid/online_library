import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base, uuid_pk


class ReviewsOrm(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = uuid_pk()
    text: Mapped[str] = mapped_column(String(5000), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )

    users: Mapped[list["UsersOrm"]] = relationship(back_populates="reviews")  # type: ignore[name-defined]
    books: Mapped[list["BooksOrm"]] = relationship(back_populates="reviews")  # type: ignore[name-defined]

    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_review_user_book"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
    )