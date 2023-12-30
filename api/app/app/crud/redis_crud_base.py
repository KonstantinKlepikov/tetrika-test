import uuid
import asyncio
from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from redis.asyncio import Redis
from app.schemas import scheme_data


SchemaDbType = TypeVar("SchemaDbType", bound=BaseModel)
SchemaReturnType = TypeVar("SchemaReturnType", bound=BaseModel)


class CRUDBase(Generic[SchemaDbType]):

    def __init__(self, schema: Type[SchemaReturnType]) -> None:
        """
        CRUD object with default methods to Create,
        Read, Update, Delete (CRUD).
        """
        self.schema = schema

    async def get(self, uuid_id: uuid.UUID, db: Redis) -> SchemaReturnType:
        """Get single document

        Args:
            uuid_id (UUID): uuid id
            db (Redis): db connection

        Returns:
            SchemaReturnType: search result
        """
        result = await db.hgetall(str(uuid_id))
        return self.schema(**result)

    async def create(
        self,
        uuid_id: uuid.UUID,
        db: Redis,
        obj_in: SchemaDbType
            ) -> None:
        """Create document

        Args:
            uuid_id (UUID): uuid id
            db (Redis): db connection
            obj_in (SchemaDbType): scheme to creare
        """
        await db.hmset(str(uuid_id), obj_in.model_dump())

    async def delete(self, uuid_id: uuid.UUID, db: Redis) -> None:
        """Remove one document

        Args:
            uuid_id (UUID): uuid id
            db (Redis): db connection
        """
        await db.delete(str(uuid_id))


class CRUDData(CRUDBase[scheme_data.Data]):
    """CRUDData
    """

    async def update_fields(
        self,
        uuid_id: uuid.UUID,
        db: Redis,
        fields: dict[str, int]
            ) -> None:
        """Incremental update one field

        Args:
            uuid_id (UUID): uuid id
            db (Redis): db connection
            fields (dict[str, int]): fields to update
        """
        u = str(uuid_id)
        pipe = db.pipeline()
        for k, v in fields.items():
            pipe.hincrby(u, k, v)
        await pipe.execute()


crud_data = CRUDData(schema=scheme_data.DataOut)