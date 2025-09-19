from pydantic import BaseModel, UUID4

class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class GenreRead(GenreBase):
    id: UUID4

    class Config:
        orm_mode = True
