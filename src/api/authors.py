from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src.dependencies.deps import get_current_active_user, DBDep
from src.models import UsersOrm, AuthorsOrm
from src.schemas.authors import AuthorRead, AuthorCreate, AuthorUpdate
from src.utilis.enums import RoleEnum

router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("/", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(payload: AuthorCreate, db: DBDep, current_user=Depends(get_current_active_user)):
    if await db.authors.exists(user_id=current_user.id):
        raise HTTPException(status_code=400, detail="Profile already exists")

    author_data = payload.model_dump(exclude_none=True)
    author_data.update({
        "id": uuid.uuid4(),
        "user_id": current_user.id,
    })

    author = await db.authors.create(author_data)
    await db.users.update(current_user.id, {"role": RoleEnum.AUTHOR})
    return author


@router.put("/{author_id}", response_model=AuthorRead)
async def update_author(author_id: uuid.UUID, payload: AuthorUpdate, db: DBDep, current_user=Depends(get_current_active_user)):
    author = await db.authors.get_one(id=author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    if author.user_id != current_user.id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated = await db.authors.update(author_id, payload.model_dump(exclude_unset=True))
    return updated


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(author_id: uuid.UUID, db: DBDep, current_user=Depends(get_current_active_user)):
    author = await db.authors.get_one(id=author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    if author.user_id != current_user.id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    await db.authors.delete(id=author_id)
    await db.users.update(author.user_id, {"role": RoleEnum.USER})
    return None
