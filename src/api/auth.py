import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies.deps import DBDep
from src.schemas.auth import Token
from src.schemas.users import UserRead, UserCreate
from src.security import hash_password, verify_password, create_access_token, settings
from src.utilis.enums import RoleEnum

router = APIRouter(prefix="/auth", tags=["Authorization and Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: DBDep):
    if await db.users.get_one(username=user.username) or await db.users.get_one(email=user.email):
        raise HTTPException(status_code=400, detail="User already exists")

    user_data_dict = user.model_dump(exclude={"password"})
    user_data_dict.update({
        "id": uuid.uuid4(),
        "hashed_password": hash_password(user.password),
        "role": RoleEnum.USER,
        "is_active": True,
    })

    new_user = await db.users.create(user_data_dict)
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(db: DBDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.get_one(username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"user_id": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
