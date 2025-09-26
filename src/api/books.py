from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from src.dependencies.database_dep import get_db
from src.dependencies.auth_and_users_dep import get_current_active_user
from src.models import AuthorsOrm, BooksOrm, GenresOrm
from src.schemas.books import BookRead, BookCreate, BookUpdate
from src.utilis.enums import RoleEnum

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in [RoleEnum.AUTHOR, RoleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Only authors or admins can create books")

    if current_user.role == RoleEnum.AUTHOR:
        result = await db.execute(select(AuthorsOrm).where(AuthorsOrm.user_id == current_user.id))
        author = result.scalar_one_or_none()
        if not author:
            raise HTTPException(status_code=400, detail="Author profile not found")
        author_id = author.id
    else:
        author_id = payload.author_id
        if not author_id:
            raise HTTPException(status_code=400, detail="Admin must provide author_id")

    book = BooksOrm(
        id=uuid.uuid4(),
        title=payload.title,
        description=payload.description,
        cover_image=payload.cover_image,
        file_path=payload.file_path,
        author_id=author_id,
    )

    if payload.genre_ids:
        genres = (await db.execute(
            select(GenresOrm).where(GenresOrm.id.in_(payload.genre_ids))
        )).scalars().all()
        book.genres = genres

    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


@router.put("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: uuid.UUID,
    payload: BookUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BooksOrm).where(BooksOrm.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if current_user.role == RoleEnum.AUTHOR:
        author_result = await db.execute(select(AuthorsOrm).where(AuthorsOrm.user_id == current_user.id))
        author = author_result.scalar_one_or_none()
        if not author or book.author_id != author.id:
            raise HTTPException(status_code=403, detail="Forbidden")

    elif current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = payload.model_dump(exclude_unset=True, exclude={"genre_ids"})
    for key, value in data.items():
        setattr(book, key, value)

    if payload.genre_ids is not None:
        genres = (await db.execute(
            select(GenresOrm).where(GenresOrm.id.in_(payload.genre_ids))
        )).scalars().all()
        book.genres = genres

    await db.commit()
    await db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BooksOrm).where(BooksOrm.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if current_user.role == RoleEnum.AUTHOR:
        author_result = await db.execute(select(AuthorsOrm).where(AuthorsOrm.user_id == current_user.id))
        author = author_result.scalar_one_or_none()
        if not author or book.author_id != author.id:
            raise HTTPException(status_code=403, detail="Forbidden")

    elif current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    await db.execute(delete(BooksOrm).where(BooksOrm.id == book_id))
    await db.commit()
    return None

