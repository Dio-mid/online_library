import uuid
from typing import Optional, Dict
from pydantic import BaseModel

class RoleBase(BaseModel):
    name: str
    permissions: Dict[str, bool] = {}

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None

class RoleRead(RoleBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
