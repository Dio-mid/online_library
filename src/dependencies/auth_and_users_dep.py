import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database_dep import get_db
from src.models import UsersOrm
from src.schemas.auth import TokenData
from src.security import decode_access_token
from src.utilis.enums import RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UsersOrm:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    data = TokenData(**payload)

    result = await db.execute(select(UsersOrm).where(UsersOrm.id == data.user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UsersOrm = Depends(get_current_user)) -> UsersOrm:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def role_checker(*allowed_roles: RoleEnum):
    async def checker(current_user: UsersOrm = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуются роли: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return checker


get_admin_user = Depends(role_checker(RoleEnum.ADMIN))
get_author_user = Depends(role_checker(RoleEnum.AUTHOR, RoleEnum.ADMIN))
get_basic_user = Depends(role_checker(RoleEnum.USER, RoleEnum.AUTHOR, RoleEnum.ADMIN))

async def self_or_admin(user_id: uuid.UUID, current_user: UsersOrm = Depends(get_current_active_user)):
    if current_user.id == user_id:
        return current_user
    if current_user.role != RoleEnum.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    return current_user
