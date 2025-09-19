import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.dependencies import get_db
from src.api.dependencies import (
    get_current_user, get_admin_user, get_author_user
)
from src.models import BooksOrm, AuthorsOrm, GenresOrm
from src.models.genres import book_genre
from src.schemas.books import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookRead])
async def list_books(db: AsyncSession = Depends(get_db)):
    query = select(BooksOrm).options(selectinload(BooksOrm.genres))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    q = (
        select(BooksOrm)
        .where(BooksOrm.id == book_id)
        .options(selectinload(BooksOrm.genres))
    )
    book = (await db.execute(q)).scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[get_author_user]
)
async def create_book(
    payload: BookCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # проверяем профиль автора
    author = (await db.execute(
        select(AuthorsOrm).where(AuthorsOrm.user_id == current_user.id)
    )).scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=400, detail="Author profile not found")

    # создаём книгу
    new_book = (await db.execute(
        insert(BooksOrm)
        .values(
            id=uuid.uuid4(),
            title=payload.title,
            description=payload.description,
            cover_image=payload.cover_image,
            file_path=payload.file_path,
            author_id=author.id,
        )
        .returning(BooksOrm)
    )).scalar_one()
    # привязываем жанры
    if payload.genre_ids:
        # проверяем существование жанров
        for gid in payload.genre_ids:
            exists = await db.execute(
                select(GenresOrm).where(GenresOrm.id == gid)
            )
            if not exists.scalar_one_or_none():
                raise HTTPException(status_code=404, detail=f"Genre {gid} not found")
            await db.execute(
                insert(book_genre).values(book_id=new_book.id, genre_id=gid)
            )
    await db.commit()

    # возвращаем с подгрузкой жанров
    return (await db.execute(
        select(BooksOrm)
        .where(BooksOrm.id == new_book.id)
        .options(selectinload(BooksOrm.genres))
    )).scalar_one()


@router.put(
    "/{book_id}",
    response_model=BookRead,
    dependencies=[get_author_user]
)
async def update_book(
    book_id: uuid.UUID,
    payload: BookUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # ищем книгу
    book = (await db.execute(
        select(BooksOrm).where(BooksOrm.id == book_id)
    )).scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # право: автор — свои книги, админ — любые
    if book.author_id != current_user.id:
        await get_admin_user(current_user, db)

    data = payload.model_dump(exclude_unset=True)
    # обновляем поля книги
    if {k: v for k, v in data.items() if k != "genre_ids"}:
        await db.execute(
            update(BooksOrm)
            .where(BooksOrm.id == book_id)
            .values(**{k: v for k, v in data.items() if k != "genre_ids"})
        )

    # обновляем связи с жанрами, если переданы
    if "genre_ids" in data:
        # удаляем старые
        await db.execute(
            delete(book_genre).where(book_genre.c.book_id == book_id)
        )
        # добавляем новые
        for gid in data["genre_ids"] or []:
            exists = await db.execute(
                select(GenresOrm).where(GenresOrm.id == gid)
            )
            if not exists.scalar_one_or_none():
                raise HTTPException(status_code=404, detail=f"Genre {gid} not found")
            await db.execute(
                insert(book_genre).values(book_id=book_id, genre_id=gid)
            )

    await db.commit()

    # возвращаем с жанрами
    return (await db.execute(
        select(BooksOrm)
        .where(BooksOrm.id == book_id)
        .options(selectinload(BooksOrm.genres))
    )).scalar_one()


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[get_admin_user]
)
async def delete_book(book_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        delete(BooksOrm).where(BooksOrm.id == book_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    await db.commit()

