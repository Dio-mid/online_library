from sqlalchemy import select
from src.models import GenresOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.entities import GenreDataMapper

class GenreRepository(BaseRepository[GenresOrm, GenreDataMapper]):
    model = GenresOrm
    mapper = GenreDataMapper
