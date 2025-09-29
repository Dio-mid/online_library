from sqlalchemy import select
from src.models import AuthorsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.entities import AuthorDataMapper


class AuthorRepository(BaseRepository[AuthorsOrm, AuthorDataMapper]):
    model = AuthorsOrm
    mapper = AuthorDataMapper
