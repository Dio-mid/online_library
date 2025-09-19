import uuid

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database import async_session_maker
from src.models import UsersOrm, RolesOrm
from src.schemas.auth import TokenData
from src.security import decode_access_token


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
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

async def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def permission_checker(permission: str):
    async def checker(current_user=Depends(get_current_active_user),
                      db: AsyncSession = Depends(get_db)):
        # загружаем роль вместе с JSON-полем permissions
        result = await db.execute(
            select(RolesOrm).where(RolesOrm.id == current_user.role_id)
        )
        role = result.scalar_one_or_none()
        if not role or not role.permissions.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}"
            )
        return current_user
    return checker

async def self_or_manage_users(
    user_id: uuid.UUID,
    current_user: UsersOrm = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.id == user_id:
        return current_user
    checker = permission_checker("can_manage_users")
    return await checker(current_user=current_user, db=db)

get_admin_user  = Depends(permission_checker("can_manage_roles"))
get_author_user = Depends(permission_checker("can_publish"))
get_basic_user  = Depends(permission_checker("can_review"))
get_favorite_user = Depends(permission_checker("can_favorite"))



