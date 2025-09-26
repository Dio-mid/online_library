import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database_dep import get_db
from src.dependencies.auth_and_users_dep import get_admin_user
from src.models import GenresOrm
from src.schemas.genres import GenreRead, GenreCreate

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("", response_model=List[GenreRead])
async def list_genres(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GenresOrm))
    return result.scalars().all()


@router.get("/{genre_id}", response_model=GenreRead)
async def get_genre(genre_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GenresOrm).where(GenresOrm.id == genre_id))
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    return genre


@router.post("", response_model=GenreRead, status_code=status.HTTP_201_CREATED, dependencies=[get_admin_user])
async def create_genre(payload: GenreCreate, db: AsyncSession = Depends(get_db)):
    stmt = insert(GenresOrm).values(id=uuid.uuid4(), name=payload.name).returning(GenresOrm)
    result = await db.execute(stmt)
    genre = result.scalar_one()
    await db.commit()
    return genre


@router.put("/{genre_id}", response_model=GenreRead, dependencies=[get_admin_user])
async def update_genre(genre_id: uuid.UUID, payload: GenreCreate, db: AsyncSession = Depends(get_db)):
    stmt = update(GenresOrm).where(GenresOrm.id == genre_id).values(name=payload.name).returning(GenresOrm)
    updated = (await db.execute(stmt)).scalar_one_or_none()
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    await db.commit()
    return updated


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[get_admin_user])
async def delete_genre(genre_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = delete(GenresOrm).where(GenresOrm.id == genre_id)
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    await db.commit()
