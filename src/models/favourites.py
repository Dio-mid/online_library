import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base, uuid_pk


class FavouritesOrm(Base):
    __tablename__ = "favourites"
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    book_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)

    user: Mapped["UsersOrm"] = relationship(back_populates="favourites") # type: ignore[name-defined]
    book: Mapped["BooksOrm"] = relationship(back_populates="favourites") # type: ignore[name-defined]

    __table_args__ = (UniqueConstraint("user_id", "book_id", name="uq_fav_user_book"),)