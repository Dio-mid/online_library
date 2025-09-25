import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    AUTHOR = "author"
    USER = "user"