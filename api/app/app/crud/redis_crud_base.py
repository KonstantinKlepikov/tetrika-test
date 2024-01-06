import json
from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from redis.asyncio import Redis
from app.schemas.scheme_data import UserOut, UsersStatus, UsersOut
from app.schemas.constraint import ProcessingResult


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
        # TODO: test me
        """
        result = await db.hget(uuid_id)
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
        # TODO: test me
        """
        await db.hmset(uuid_id, obj_in.model_dump())

    async def update(
        self,
        uuid_id: str,
        db: Redis,
        obj_in: dict[str, int]
            ) -> None:
        """Update document fields

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection
            obj_in (dict[str, int]): fields to update
        # TODO: test me
        """
        await db.hmset(uuid_id, obj_in)

    async def delete(self, uuid_id: str, db: Redis) -> None:
        """Remove one document

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection
        # TODO: test me
        """
        await db.delete(uuid_id)


class CRUDData(CRUDBase[UsersStatus]):
    """CRUDData
    """

    async def get_result(self, uuid_id: str, db: Redis) -> UsersOut:
        """Get result of data processing

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection

        Returns:
            UsersOut: search result
        # TODO: test me
        """
        result = await db.hvals(uuid_id)
        data = []
        for i in result:
            try:
                d = json.loads(i.decode('utf-8'))
                if isinstance(d, dict):
                    data.append(UserOut(**d))
            except:  # FIXME: add json loads exception
                pass

        return self.schema(result=data)

    async def update_num_fields_incremental(
        self,
        uuid_id: str,
        db: Redis,
        obj_in: dict[str, int]
            ) -> None:
        """Incremental update many fields

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection
            obj_in (dict[str, int]): fields to update
        # TODO: test me
        """
        pipe = db.pipeline()
        for k, v in obj_in.items():
            pipe.hincrby(uuid_id, k, v)
        await pipe.execute()

    async def set_user_json(
        self,
        uuid_id: str,
        db: Redis,
        obj_in: UserOut
            ) -> None:
        """Set field by given uuid_id

        Args:
            uuid_id (str): uuid id
            db (Redis): redis connection
            obj_in (UserOut): seting field
        # TODO: test me
        """
        await db.hset(uuid_id, obj_in.userId, obj_in.model_dump_json())

    async def get_status(
        self,
        uuid_id: str,
        db: Redis
            ) -> UsersStatus:
        """Get fields of single document

        Args:
            uuid_id (str): uuid id
            db (Redis): db connection

        Returns:
            UsersStatus: search result
        # TODO: test me
        """
        result = await db.hmget(uuid_id, *UsersStatus.model_fields.keys())
        if all(result):
            return UsersStatus(
                data_in=int(result[0]),
                data_out=int(result[1]),
                errors=int(result[2]),
                result=ProcessingResult(result[3].decode('utf-8')),
                    )
        return UsersStatus()


crud_data = CRUDData(schema=UsersOut)
