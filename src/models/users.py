import uuid

from sqlalchemy import String, Boolean, text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, uuid_pk
from src.utilis.enums import RoleEnum



class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.USER # type: ignore[name-defined]
    )

    author: Mapped["AuthorsOrm"] = relationship(back_populates="user", uselist=False) # type: ignore[name-defined]
    reviews: Mapped[list["ReviewsOrm"]] = relationship(back_populates="user") # type: ignore[name-defined]
    favourites: Mapped[list["FavouritesOrm"]] = relationship(back_populates="user") # type: ignore[name-defined]
