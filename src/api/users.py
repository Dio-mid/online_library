import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.deps import get_current_active_user, self_or_admin, DBDep
from src.models import UsersOrm
from src.schemas.users import UserRead, UserUpdateSelf, UserUpdateAdmin
from src.security import hash_password
from src.utilis.enums import RoleEnum

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserRead])
async def list_users(db: DBDep, current_user=Depends(get_current_active_user)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await db.users.get_many()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, db: DBDep, current_user=Depends(get_current_active_user)):
    if current_user.role != RoleEnum.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = await db.users.get_one(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(payload: UserUpdateSelf, db: DBDep, current_user=Depends(get_current_active_user)):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    await db.users.update(current_user.id, update_data)
    return await db.users.get_one(id=current_user.id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user_as_admin(user_id: uuid.UUID, payload: UserUpdateAdmin, db: DBDep, current_user=Depends(get_current_active_user)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    updated = await db.users.update(user_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, db: DBDep, current_user=Depends(get_current_active_user)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    deleted = await db.users.delete(id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    return None
