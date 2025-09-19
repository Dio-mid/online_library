import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.api.dependencies import (
    get_current_active_user,
    get_basic_user
)
from src.models import ReviewsOrm, BooksOrm
from src.schemas.reviews import ReviewCreate, ReviewRead, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.get("", response_model=List[ReviewRead])
async def list_reviews(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReviewsOrm))
    return result.scalars().all()

@router.get("/{review_id}", response_model=ReviewRead)
async def get_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ReviewsOrm).where(ReviewsOrm.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.post(
    "",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[get_basic_user]
)
async def create_review(
    payload: ReviewCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # проверка книги
    book_exists = await db.execute(
        select(BooksOrm).where(BooksOrm.id == payload.book_id)
    )
    if not book_exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Book not found")

    # уникальность пользователя+книги
    exists = await db.execute(
        select(ReviewsOrm).where(
            (ReviewsOrm.user_id == current_user.id) &
            (ReviewsOrm.book_id == payload.book_id)
        )
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Review already exists")

    stmt = (
        insert(ReviewsOrm)
        .values(
            id=uuid.uuid4(),
            text=payload.text,
            rating=payload.rating,
            user_id=current_user.id,
            book_id=payload.book_id
        )
        .returning(ReviewsOrm)
    )
    review = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return review

@router.put(
    "/{review_id}",
    response_model=ReviewRead,
    dependencies=[get_basic_user]
)
async def update_review(
    review_id: uuid.UUID,
    payload: ReviewUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ReviewsOrm).where(ReviewsOrm.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden to update")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No data to update")

    stmt = (
        update(ReviewsOrm)
        .where(ReviewsOrm.id == review_id)
        .values(**data)
        .returning(ReviewsOrm)
    )
    updated = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return updated

@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[get_basic_user]
)
async def delete_review(
    review_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ReviewsOrm).where(ReviewsOrm.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden to delete")

    await db.execute(delete(ReviewsOrm).where(ReviewsOrm.id == review_id))
    await db.commit()
