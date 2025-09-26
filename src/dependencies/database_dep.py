import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Универсальная фабрика UUID PK
def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )