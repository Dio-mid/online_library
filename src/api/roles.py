import uuid

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db, get_admin_user
from src.models import RolesOrm
from src.schemas.roles import RoleRead, RoleUpdate, RoleCreate

router = APIRouter(prefix="/roles", tags=["Roles"], dependencies=[get_admin_user])


@router.get("", response_model=list[RoleRead])
async def list_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RolesOrm))
    return result.scalars().all()

@router.get("/{role_id}", response_model=RoleRead)
async def get_role(role_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RolesOrm).where(RolesOrm.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.post("", response_model=RoleRead)
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    stmt = (
        insert(RolesOrm)
        .values(**role.model_dump())
        .returning(RolesOrm)
    )
    result = await db.execute(stmt)
    new_role = result.scalar_one()
    await db.commit()
    return new_role

@router.put("/{role_id}", response_model=RoleRead)
async def update_role(role_id: uuid.UUID, role_data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    update_data = role_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")

    stmt = (
        update(RolesOrm)
        .where(RolesOrm.id == role_id)
        .values(**update_data)
        .returning(RolesOrm)
    )

    result = await db.execute(stmt)
    updated_role = result.scalar_one_or_none()

    if not updated_role:
        raise HTTPException(status_code=404, detail="Role not found")

    await db.commit()
    return updated_role

@router.delete("/{role_id}")
async def delete_role(role_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = delete(RolesOrm).where(RolesOrm.id == role_id).returning(RolesOrm.id)
    result = await db.execute(stmt)
    deleted_id = result.scalar_one_or_none()
    if not deleted_id:
        raise HTTPException(status_code=404, detail="Role not found")
    await db.commit()
    return {"detail": "Role deleted"}