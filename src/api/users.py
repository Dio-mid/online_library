import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import (
    get_db,
    get_current_active_user,
    permission_checker, self_or_manage_users,
)
from src.models import UsersOrm
from src.schemas.users import UserRead, UserUpdate
from src.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=List[UserRead],
    dependencies=[Depends(permission_checker("can_manage_users"))],
)
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UsersOrm))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    _ok: UsersOrm = Depends(self_or_manage_users),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UsersOrm).where(UsersOrm.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate = Body(...),
    current_user: UsersOrm = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Проверяем исходный профиль
    result = await db.execute(select(UsersOrm).where(UsersOrm.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_self = current_user.id == user_id
    if not is_self:
        await permission_checker("can_manage_users")(current_user=current_user, db=db)
        is_admin = True
    else:
        is_admin = False

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    # Если пользователь меняет пароль — хешируем
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    # только админ может дёргать role_id и is_active
    if not is_admin:
        update_data.pop("role_id", None)
        update_data.pop("is_active", None)

    stmt = (
        update(UsersOrm)
        .where(UsersOrm.id == user_id)
        .values(**update_data)
        .returning(UsersOrm)
    )
    updated = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return updated


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(permission_checker("can_manage_users"))],
)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = delete(UsersOrm).where(UsersOrm.id == user_id).returning(UsersOrm.id)
    deleted = (await db.execute(stmt)).scalar_one_or_none()
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    await db.commit()
