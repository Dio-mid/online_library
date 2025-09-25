import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base


class ReviewsOrm(Base):
    __tablename__ = "reviews"
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    book_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)

    text: Mapped[str] = mapped_column(String(5000), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user: Mapped["UsersOrm"] = relationship(back_populates="reviews") # type: ignore[name-defined]
    book: Mapped["BooksOrm"] = relationship(back_populates="reviews") # type: ignore[name-defined]

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
    )
