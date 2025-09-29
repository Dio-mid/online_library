import uuid
from sqlalchemy import select, delete
from src.models import FavouritesOrm, BooksOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.entities import FavouriteDataMapper


class FavouriteRepository(BaseRepository[FavouritesOrm, FavouriteDataMapper]):
    model = FavouritesOrm
    mapper = FavouriteDataMapper

    async def exists(self, user_id: uuid.UUID, book_id: uuid.UUID) -> bool:
        stmt = select(1).where(
            FavouritesOrm.user_id == user_id,
            FavouritesOrm.book_id == book_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() is not None