from src.models import AuthorsOrm, BooksOrm, FavouritesOrm, GenresOrm, ReviewsOrm, UsersOrm
from src.schemas import AuthorRead, FavouriteRead, GenreRead
from src.schemas.users import UserInDB
from src.schemas.books import BookInDB
from src.schemas.reviews import ReviewInDB
from src.repositories.mappers.base import DataMapper


class AuthorDataMapper(DataMapper):
    db_model = AuthorsOrm
    schema = AuthorRead

class BookDataMapper(DataMapper):
    db_model = BooksOrm
    schema = BookInDB

class FavouriteDataMapper(DataMapper):
    db_model = FavouritesOrm
    schema = FavouriteRead

class GenreDataMapper(DataMapper):
    db_model = GenresOrm
    schema = GenreRead

class ReviewDataMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewInDB

class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = UserInDB
