import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database_dep import get_db
from src.dependencies.auth_and_users_dep import get_current_active_user
from src.models import BooksOrm, ReviewsOrm
from src.schemas.reviews import ReviewRead, ReviewCreate, ReviewUpdate
from src.utilis.enums import RoleEnum

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BooksOrm).where(BooksOrm.id == payload.book_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Book not found")

    existing = await db.execute(
        select(ReviewsOrm).where(
            ReviewsOrm.book_id == payload.book_id,
            ReviewsOrm.user_id == current_user.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Review already exists")

    stmt = (
        insert(ReviewsOrm)
        .values(
            book_id=payload.book_id,
            user_id=current_user.id,
            rating=payload.rating,
            text=payload.text,
        )
        .returning(ReviewsOrm)
    )
    review = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return review


@router.put("/{book_id}", response_model=ReviewRead)
async def update_review(
    book_id: uuid.UUID,
    payload: ReviewUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == RoleEnum.ADMIN:
        target_user_id = payload.user_id or current_user.id
    else:
        target_user_id = current_user.id

    result = await db.execute(
        select(ReviewsOrm).where(
            ReviewsOrm.book_id == book_id,
            ReviewsOrm.user_id == target_user_id
        )
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    stmt = (
        update(ReviewsOrm)
        .where(ReviewsOrm.book_id == book_id, ReviewsOrm.user_id == target_user_id)
        .values(**payload.model_dump(exclude_unset=True, exclude={"user_id"}))
        .returning(ReviewsOrm)
    )
    updated = (await db.execute(stmt)).scalar_one_or_none()
    if not updated:
        raise HTTPException(status_code=404, detail="Review not found")

    await db.commit()
    return updated


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    book_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID | None = None,
):
    target_user_id = current_user.id

    if current_user.role == RoleEnum.ADMIN:
        if not user_id:
            raise HTTPException(status_code=400, detail="Admin must provide user_id")
        target_user_id = user_id

    result = await db.execute(
        delete(ReviewsOrm).where(
            ReviewsOrm.book_id == book_id,
            ReviewsOrm.user_id == target_user_id
        ).returning(ReviewsOrm)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    await db.commit()
    return None

