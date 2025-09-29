from src.repositories.base import BaseRepository
from src.repositories.mappers.entities import UserDataMapper
from src.models import UsersOrm


class UserRepository(BaseRepository[UsersOrm, UserDataMapper]):
    model = UsersOrm
    mapper = UserDataMapper
