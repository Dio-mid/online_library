from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src.database import get_db
from src.dependencies.dependencies import get_current_active_user, RoleEnum
from src.models import UsersOrm, AuthorsOrm
from src.schemas.authors import AuthorRead, AuthorCreate, AuthorUpdate

router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("/", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(
    payload: AuthorCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AuthorsOrm).where(AuthorsOrm.user_id == current_user.id))
    if result.scalar_one_or_none():
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

    await db.execute(
        update(UsersOrm)
        .where(UsersOrm.id == current_user.id)
        .values(role=RoleEnum.AUTHOR)
    )

    await db.commit()
    return author


@router.put("/{author_id}", response_model=AuthorRead)
async def update_author(
    author_id: uuid.UUID,
    payload: AuthorUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AuthorsOrm).where(AuthorsOrm.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    if author.user_id != current_user.id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

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


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AuthorsOrm).where(AuthorsOrm.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    if author.user_id != current_user.id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    await db.execute(delete(AuthorsOrm).where(AuthorsOrm.id == author_id))

    await db.execute(
        update(UsersOrm)
        .where(UsersOrm.id == author.user_id)
        .values(role=RoleEnum.USER)
    )

    await db.commit()
    return None
