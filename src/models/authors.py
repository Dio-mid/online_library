import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base, uuid_pk


class AuthorsOrm(Base):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    bio: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    profile_picture: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    user: Mapped[list["UserOrm"]] = relationship(back_populates="authors")  # type: ignore[name-defined]
    books: Mapped[list["BooksOrm"]] = relationship(  # type: ignore[name-defined]
        back_populates="authors", cascade="all,delete-orphan", passive_deletes=True
    )