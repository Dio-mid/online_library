import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies.dependencies import get_current_active_user, get_basic_user
from src.models import FavouritesOrm, BooksOrm
from src.schemas.favourites import FavouriteRead, FavouriteCreate

router = APIRouter(prefix="/favourites", tags=["Favourites"])


@router.get("", response_model=List[FavouriteRead])
async def list_favourites(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FavouritesOrm).where(FavouritesOrm.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("", response_model=FavouriteRead, status_code=status.HTTP_201_CREATED)
async def add_favourite(
    payload: FavouriteCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    exists = await db.execute(
        select(BooksOrm).where(BooksOrm.id == payload.book_id)
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Book not found")

    fav_exists = await db.execute(
        select(FavouritesOrm).where(
            FavouritesOrm.user_id == current_user.id,
            FavouritesOrm.book_id == payload.book_id
        )
    )
    if fav_exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already in favourites")

    stmt = (
        insert(FavouritesOrm)
        .values(user_id=current_user.id, book_id=payload.book_id)
        .returning(FavouritesOrm)
    )
    favourite = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return favourite


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favourite(
    book_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        delete(FavouritesOrm)
        .where(
            FavouritesOrm.user_id == current_user.id,
            FavouritesOrm.book_id == book_id
        )
        .returning(FavouritesOrm)
    )
    deleted = (await db.execute(stmt)).scalar_one_or_none()
    if not deleted:
        raise HTTPException(status_code=404, detail="Favourite not found")

    await db.commit()
    return None

