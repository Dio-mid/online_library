import uuid
from typing import Optional, List
from sqlalchemy import select
from src.models import BooksOrm, GenresOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.entities import BookDataMapper


class BookRepository(BaseRepository[BooksOrm, BookDataMapper]):
    model = BooksOrm
    mapper = BookDataMapper

    async def create_with_genres(self, title, description, cover_image, file_path, author_id, genre_ids=None):
        book = BooksOrm(
            id=uuid.uuid4(),
            title=title,
            description=description,
            cover_image=cover_image,
            file_path=file_path,
            author_id=author_id,
        )

        if genre_ids:
            genres = (
                await self.session.execute(
                    select(GenresOrm).where(GenresOrm.id.in_(genre_ids))
                )
            ).scalars().all()
            book.genres = genres

        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book)
        return book

    async def update_with_genres(self, book: BooksOrm, data: dict, genre_ids=None):
        for key, value in data.items():
            setattr(book, key, value)

        if genre_ids is not None:
            genres = (
                await self.session.execute(
                    select(GenresOrm).where(GenresOrm.id.in_(genre_ids))
                )
            ).scalars().all()
            book.genres = genres

        await self.session.commit()
        await self.session.refresh(book)
        return book
