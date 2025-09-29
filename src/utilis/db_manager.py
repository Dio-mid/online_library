from src.repositories.users import UserRepository
from src.repositories.authors import AuthorRepository
from src.repositories.books import BookRepository
from src.repositories.favourites import FavouriteRepository
from src.repositories.genres import GenreRepository
from src.repositories.reviews import ReviewRepository

class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UserRepository(self.session)
        self.authors = AuthorRepository(self.session)
        self.books = BookRepository(self.session)
        self.favourites = FavouriteRepository(self.session)
        self.genres = GenreRepository(self.session)
        self.reviews = ReviewRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()