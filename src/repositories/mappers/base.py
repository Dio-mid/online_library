from typing import TypeVar
from pydantic import BaseModel
from src.database import Base

DBModelType = TypeVar("DBModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper:
    db_model: type[DBModelType] = None
    schema: type[SchemaType] = None

    @classmethod
    def map_to_domain_entity(cls, data):
        if cls.schema is None:
            raise RuntimeError("Mapper.schema is not set")
        if isinstance(data, cls.schema):
            return data
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data):
        if cls.db_model is None:
            raise RuntimeError("Mapper.db_model is not set")

        if hasattr(data, "model_dump"):
            payload = data.model_dump(exclude_none=True)
        elif isinstance(data, dict):
            payload = {k: v for k, v in data.items() if v is not None}
        else:
            payload = dict(data.__dict__)

        return cls.db_model(**payload)
