import uuid
from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from redis.asyncio import Redis
from app.schemas.scheme_data import UserOut, UsersStatus, UsersOut


SchemaDbType = TypeVar("SchemaDbType", bound=BaseModel)
SchemaReturnType = TypeVar("SchemaReturnType", bound=BaseModel)


class CRUDBase(Generic[SchemaDbType]):
    """Base class for redis crud
    """

    def __init__(self, schema: Type[SchemaReturnType]) -> None:
        """
        CRUD object with default methods to Create,
        Read, Update, Delete (CRUD).
        """
        self.schema = schema

    async def get(self, uuid_id: str, db: Redis) -> SchemaReturnType:
        """Get single document

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection

        Returns:
            SchemaReturnType: search result
        """
        result = await db.hgetall(uuid_id)
        return self.schema(**result)

    async def create(
        self,
        uuid_id: str,
        db: Redis,
        obj_in: SchemaDbType
            ) -> None:
        """Create document

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection
            obj_in (SchemaDbType): scheme to creare
        """
        await db.hmset(uuid_id, obj_in.model_dump())

    async def delete(self, uuid_id: str, db: Redis) -> None:
        """Remove one document

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection
        """
        await db.delete(uuid_id)


class CRUDData(CRUDBase[UsersStatus]):
    """CRUDData
    """

    async def update_fields(
        self,
        uuid_id: str,
        db: Redis,
        fields: dict[str, int]
            ) -> None:
        """Incremental update many fields

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection
            fields (dict[str, int]): fields to update
        """
        pipe = db.pipeline()
        for k, v in fields.items():
            pipe.hincrby(uuid_id, k, v)
        await pipe.execute()

    async def set_field(
        self,
        uuid_id: str,
        db: Redis,
        field: UserOut
            ) -> None:
        """Set field by given uuid_id

        Args:
            uuid_id (str): uuid id
            db (Redis): redis connection
            field (UserOut): seting field
        """
        await db.hset(uuid_id, field.userId, field.model_dump_json())


crud_data = CRUDData(schema=UsersOut)
