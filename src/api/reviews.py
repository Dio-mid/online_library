import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.deps import get_current_active_user, DBDep
from src.models import BooksOrm, ReviewsOrm
from src.schemas.reviews import ReviewRead, ReviewCreate, ReviewUpdate
from src.utilis.enums import RoleEnum

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(payload: ReviewCreate, db: DBDep, current_user=Depends(get_current_active_user)):
    if not await db.books.exists(id=payload.book_id):
        raise HTTPException(status_code=404, detail="Book not found")

    if await db.reviews.exists(book_id=payload.book_id, user_id=current_user.id):
        raise HTTPException(status_code=400, detail="Review already exists")

    review_data = {
        "book_id": payload.book_id,
        "text": payload.text,
        "rating": payload.rating,
        "user_id": current_user.id
    }
    review = await db.reviews.create(review_data)
    return review


@router.put("/{book_id}", response_model=ReviewRead)
async def update_review(book_id: uuid.UUID, payload: ReviewUpdate, db: DBDep, current_user=Depends(get_current_active_user)):
    if current_user.role == RoleEnum.ADMIN:
        target_user_id = payload.user_id or current_user.id
    else:
        target_user_id = current_user.id

    review = await db.reviews.get_one(book_id=book_id, user_id=target_user_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    updated = await db.reviews.update(
        {"book_id": book_id, "user_id": target_user_id},
        payload.model_dump(exclude_unset=True, exclude={"user_id"})
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Review not found")

    return updated


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(book_id: uuid.UUID, db: DBDep, current_user=Depends(get_current_active_user), user_id: uuid.UUID | None = None):
    target_user_id = current_user.id
    if current_user.role == RoleEnum.ADMIN:
        if not user_id:
            raise HTTPException(status_code=400, detail="Admin must provide user_id")
        target_user_id = user_id

    deleted = await db.reviews.delete(book_id=book_id, user_id=target_user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")

    return None
