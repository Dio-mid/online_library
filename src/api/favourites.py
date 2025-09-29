import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.deps import get_current_active_user, get_basic_user, DBDep
from src.models import FavouritesOrm, BooksOrm
from src.schemas.favourites import FavouriteRead, FavouriteCreate

router = APIRouter(prefix="/favourites", tags=["Favourites"])


@router.get("", response_model=List[FavouriteRead])
async def list_favourites(db: DBDep, current_user=Depends(get_current_active_user)):
    return await db.favourites.get_many(user_id=current_user.id)


@router.post("", response_model=FavouriteRead, status_code=status.HTTP_201_CREATED)
async def add_favourite(payload: FavouriteCreate, db: DBDep, current_user=Depends(get_current_active_user)):
    if not await db.books.exists(id=payload.book_id):
        raise HTTPException(status_code=404, detail="Book not found")

    if await db.favourites.exists(user_id=current_user.id, book_id=payload.book_id):
        raise HTTPException(status_code=400, detail="Already in favourites")

    fav_data = {
        "book_id": payload.book_id,
        "user_id": current_user.id
    }
    fav = await db.favourites.create(fav_data)
    return fav


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favourite(book_id: uuid.UUID, db: DBDep, current_user=Depends(get_current_active_user)):
    deleted = await db.favourites.delete(user_id=current_user.id, book_id=book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Favourite not found")
    return None
