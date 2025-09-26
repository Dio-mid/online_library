import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database_dep import get_db
from src.dependencies.auth_and_users_dep import get_current_active_user, self_or_admin
from src.models import UsersOrm
from src.schemas.users import UserRead, UserUpdateSelf, UserUpdateAdmin
from src.security import hash_password
from src.utilis.enums import RoleEnum

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserRead], dependencies=[Depends(role_checker := lambda: None)])
async def list_users(db: AsyncSession = Depends(get_db), current_user: UsersOrm = Depends(get_current_active_user)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    result = await db.execute(select(UsersOrm))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, _ok: UsersOrm = Depends(self_or_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UsersOrm).where(UsersOrm.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(payload: UserUpdateSelf, current_user: UsersOrm = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update")

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    await db.execute(update(UsersOrm).where(UsersOrm.id == current_user.id).values(**update_data))
    await db.commit()
    refreshed = (await db.execute(select(UsersOrm).where(UsersOrm.id == current_user.id))).scalar_one()
    return refreshed


@router.patch("/{user_id}", response_model=UserRead)
async def update_user_as_admin(user_id: uuid.UUID, payload: UserUpdateAdmin, current_user: UsersOrm = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update")

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    await db.execute(update(UsersOrm).where(UsersOrm.id == user_id).values(**update_data))
    await db.commit()
    updated = (await db.execute(select(UsersOrm).where(UsersOrm.id == user_id))).scalar_one_or_none()
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, current_user: UsersOrm = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = delete(UsersOrm).where(UsersOrm.id == user_id)
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.commit()
