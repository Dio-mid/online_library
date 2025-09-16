import uuid
from typing import Optional

from sqlalchemy import String, Boolean, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database import Base, uuid_pk


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))

    role_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    role: Mapped[Optional["RolesOrm"]] = relationship(back_populates="users")

    # one-to-one с Author (обратная связь)
    author: Mapped[Optional["AuthorsOrm"]] = relationship(  # type: ignore[name-defined]
        back_populates="users", uselist=False, cascade="all,delete", passive_deletes=True
    )

    reviews: Mapped[list["ReviewsOrm"]] = relationship(  # type: ignore[name-defined]
        back_populates="users", cascade="all,delete-orphan", passive_deletes=True
    )
    favourites: Mapped[list["FavouritesOrm"]] = relationship(  # type: ignore[name-defined]
        back_populates="users", cascade="all,delete-orphan", passive_deletes=True
    )