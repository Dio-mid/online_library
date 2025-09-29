from typing import Type, TypeVar, Generic, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from pydantic import BaseModel
from src.database import Base
from src.repositories.mappers.base import DataMapper

DBModelType = TypeVar("DBModelType", bound=Base)
MapperType = TypeVar("MapperType", bound=DataMapper)

class BaseRepository(Generic[DBModelType, MapperType]):
    model: Type[DBModelType] = None
    mapper: Type[MapperType] = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_one(self, *filters, **filter_by) -> Optional[DBModelType]:
        stmt = select(self.model).filter(*filters).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many(self, *filters, **filter_by) -> List[DBModelType]:
        stmt = select(self.model).filter(*filters).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def exists(self, *filters, **filter_by) -> bool:
        stmt = select(self.model.id).filter(*filters).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.first() is not None

    async def create(self, obj):
        if isinstance(obj, self.model):
            db_obj = obj
        elif hasattr(obj, "model_dump"):
            db_obj = self.model(**obj.model_dump())
        elif isinstance(obj, dict):
            db_obj = self.model(**obj)
        else:
            db_obj = self.model(**obj)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, entity_id, update_data: dict):
        obj = await self.session.get(self.model, entity_id)
        if obj is None:
            return None

        if hasattr(update_data, "model_dump"):
            update_data = update_data.model_dump(exclude_unset=True)

        for key, val in update_data.items():
            if hasattr(obj, key):
                setattr(obj, key, val)

        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, *filters, **filter_by) -> bool:
        stmt = delete(self.model).filter(*filters).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
