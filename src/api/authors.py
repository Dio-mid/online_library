import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.api.dependencies import (
    get_current_active_user,
    get_admin_user,
    get_author_user,
)
from src.models import AuthorsOrm
from src.schemas.authors import AuthorCreate, AuthorRead, AuthorUpdate

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.get("", response_model=List[AuthorRead])
async def list_authors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuthorsOrm))
    return result.scalars().all()


@router.get("/{author_id}", response_model=AuthorRead)
async def get_author(
    author_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AuthorsOrm).where(AuthorsOrm.id == author_id)
    )
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.post(
    "",
    response_model=AuthorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[get_author_user],
)
async def create_author(
    payload: AuthorCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Проверяем, что профиль ещё не создан
    exists = await db.execute(
        select(AuthorsOrm).where(AuthorsOrm.user_id == current_user.id)
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Profile already exists")

    stmt = (
        insert(AuthorsOrm)
        .values(
            id=uuid.uuid4(),
            user_id=current_user.id,
            bio=payload.bio,
            profile_picture=payload.profile_picture,
        )
        .returning(AuthorsOrm)
    )
    author = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return author


@router.put(
    "/{author_id}",
    response_model=AuthorRead,
    dependencies=[get_author_user],  # must have can_publish
)
async def update_author(
    author_id: uuid.UUID,
    payload: AuthorUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Ищем профиль
    result = await db.execute(
        select(AuthorsOrm).where(AuthorsOrm.id == author_id)
    )
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    if author.user_id != current_user.id:
        # поднимем ошибку, если нет can_manage_roles
        await get_admin_user(current_user, db)

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No data to update")

    stmt = (
        update(AuthorsOrm)
        .where(AuthorsOrm.id == author_id)
        .values(**data)
        .returning(AuthorsOrm)
    )
    updated = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return updated


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[get_admin_user],
)
async def delete_author(
    author_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = delete(AuthorsOrm).where(AuthorsOrm.id == author_id).returning(AuthorsOrm.id)
    deleted = (await db.execute(stmt)).scalar_one_or_none()
    if not deleted:
        raise HTTPException(status_code=404, detail="Author not found")
    await db.commit()
