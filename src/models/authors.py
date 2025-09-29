import uuid
from typing import Optional, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base
from src.utilis.columns import uuid_pk


class AuthorsOrm(Base):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    profile_picture: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    user: Mapped["UsersOrm"] = relationship(back_populates="author") # type: ignore[name-defined]
    books: Mapped[List["BooksOrm"]] = relationship(back_populates="author", cascade="all,delete-orphan", passive_deletes=True) # type: ignore[name-defined]
