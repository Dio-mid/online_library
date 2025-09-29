from uuid import UUID
from pydantic import BaseModel

class FavouriteCreate(BaseModel):
    book_id: UUID

class FavouriteRead(BaseModel):
    user_id: UUID
    book_id: UUID

    model_config = {"from_attributes": True}
