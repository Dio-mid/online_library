import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.deps import get_admin_user, DBDep
from src.models import GenresOrm
from src.schemas.genres import GenreRead, GenreCreate

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("", response_model=List[GenreRead])
async def list_genres(db: DBDep):
    return await db.genres.get_many()


@router.get("/{genre_id}", response_model=GenreRead)
async def get_genre(genre_id: uuid.UUID, db: DBDep):
    genre = await db.genres.get_one(id=genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.post("", response_model=GenreRead, status_code=status.HTTP_201_CREATED, dependencies=[get_admin_user])
async def create_genre(payload: GenreCreate, db: DBDep):
    genre_data = payload.model_copy(update={"id": uuid.uuid4()})
    genre = await db.genres.create(genre_data)
    return genre


@router.put("/{genre_id}", response_model=GenreRead, dependencies=[get_admin_user])
async def update_genre(genre_id: uuid.UUID, payload: GenreCreate, db: DBDep):
    updated = await db.genres.update(genre_id, payload.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Genre not found")
    return updated


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[get_admin_user])
async def delete_genre(genre_id: uuid.UUID, db: DBDep):
    deleted = await db.genres.delete(id=genre_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Genre not found")
    return None
