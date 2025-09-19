import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db, get_favorite_user
from src.api.dependencies import (
    get_current_active_user,
    permission_checker
)
from src.models import FavouritesOrm, BooksOrm
from src.schemas.favourites import FavouriteCreate, FavouriteRead


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

@router.post(
    "",
    response_model=FavouriteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[get_favorite_user]
)
async def add_favourite(
    payload: FavouriteCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # проверка книги
    book_exists = await db.execute(
        select(BooksOrm).where(BooksOrm.id == payload.book_id)
    )
    if not book_exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Book not found")

    # уникальность пары user+book
    exists = await db.execute(
        select(FavouritesOrm).where(
            (FavouritesOrm.user_id == current_user.id) &
            (FavouritesOrm.book_id == payload.book_id)
        )
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already in favourites")

    stmt = (
        insert(FavouritesOrm)
        .values(
            id=uuid.uuid4(),
            user_id=current_user.id,
            book_id=payload.book_id
        )
        .returning(FavouritesOrm)
    )
    fav = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return fav

@router.delete(
    "/{favourite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[get_favorite_user]
)
async def remove_favourite(
    favourite_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FavouritesOrm).where(FavouritesOrm.id == favourite_id)
    )
    fav = result.scalar_one_or_none()
    if not fav or fav.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Favourite not found")

    await db.execute(delete(FavouritesOrm).where(FavouritesOrm.id == favourite_id))
    await db.commit()
