import uuid

from sqlalchemy import String, JSON, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, uuid_pk


class RolesOrm(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    permissions: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    users: Mapped[list["UsersOrm"]] = relationship(back_populates="roles", cascade="all,delete", passive_deletes=True)

    __table_args__ = (
        CheckConstraint("name IN ('admin','author','user')", name="ck_role_name_choices"),
    )