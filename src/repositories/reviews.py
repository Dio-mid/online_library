import uuid
from sqlalchemy import select, delete, update
from src.models import ReviewsOrm, BooksOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.entities import ReviewDataMapper


class ReviewRepository(BaseRepository[ReviewsOrm, ReviewDataMapper]):
    model = ReviewsOrm
    mapper = ReviewDataMapper

    async def exists(self, book_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(1).where(
            ReviewsOrm.book_id == book_id,
            ReviewsOrm.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() is not None