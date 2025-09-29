from pydantic import BaseModel, UUID4

class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class GenreRead(GenreBase):
    id: UUID4

    model_config = {"from_attributes": True}
