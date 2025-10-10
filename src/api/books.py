import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache

from src.dependencies.deps import get_current_active_user, DBDep
from src.schemas.books import BookRead, BookCreate, BookUpdate
from src.utilis.enums import RoleEnum

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/{book_id}", response_model=BookRead)
@cache(expire=10*60)
async def get_book(book_id: uuid.UUID, db: DBDep):
    book = await db.books.get_one(id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, db: DBDep, current_user=Depends(get_current_active_user)):
    if current_user.role not in [RoleEnum.AUTHOR, RoleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Only authors or admins can create books")

    if current_user.role == RoleEnum.AUTHOR:
        author = await db.authors.get_one(user_id=current_user.id)
        if not author:
            raise HTTPException(status_code=400, detail="Author profile not found")
        author_id = author.id
    else:
        if not payload.author_id:
            raise HTTPException(status_code=400, detail="Admin must provide author_id")
        author_id = payload.author_id

    book = await db.books.create_with_genres(
        title=payload.title,
        description=payload.description,
        cover_image=payload.cover_image,
        file_path=payload.file_path,
        author_id=author_id,
        genre_ids=payload.genre_ids,
    )
    return book


@router.put("/{book_id}", response_model=BookRead)
async def update_book(book_id: uuid.UUID, payload: BookUpdate, db: DBDep, current_user=Depends(get_current_active_user)):
    book = await db.books.get_one(id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if current_user.role == RoleEnum.AUTHOR:
        author = await db.authors.get_one(user_id=current_user.id)
        if not author or book.author_id != author.id:
            raise HTTPException(status_code=403, detail="Forbidden")
    elif current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated = await db.books.update_with_genres(book, payload.model_dump(exclude_unset=True, exclude={"genre_ids"}), payload.genre_ids)
    return updated


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: uuid.UUID, db: DBDep, current_user=Depends(get_current_active_user)):
    book = await db.books.get_one(id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if current_user.role == RoleEnum.AUTHOR:
        author = await db.authors.get_one(user_id=current_user.id)
        if not author or book.author_id != author.id:
            raise HTTPException(status_code=403, detail="Forbidden")
    elif current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    await db.books.delete(id=book_id)
    return None
