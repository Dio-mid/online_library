import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.schemas.auth import Token
from src.schemas.users import UserCreate, UserRead
from src.models import UsersOrm
from src.api.dependencies import get_db
from src.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authorization and Authentication"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(
        select(UsersOrm).where(
            (UsersOrm.username == user.username) |
            (UsersOrm.email == user.email)
        )
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")

    stmt = insert(UsersOrm).values(
        id=uuid.uuid4(),
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        role_id=user.role_id
    ).returning(UsersOrm)
    new_user = (await db.execute(stmt)).scalar_one()
    await db.commit()
    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UsersOrm).where(UsersOrm.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"user_id": str(user.id), "role_id": str(user.role_id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
