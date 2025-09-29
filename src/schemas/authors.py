from typing import Optional
from pydantic import BaseModel, UUID4, Field

class AuthorBase(BaseModel):
    bio: Optional[str]
    profile_picture: Optional[str]

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(AuthorBase):
    pass

class AuthorRead(AuthorBase):
    id: UUID4
    user_id: UUID4

    model_config = {"from_attributes": True}
