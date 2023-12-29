import uuid
import random
from pydantic import BaseModel, UUID4
from app.schemas.constraint import ProcessingResult


rnd = random.Random()
rnd.seed(123)
UUID_ID = uuid.UUID(int=rnd.getrandbits(128), version=4)


class UserId(BaseModel):
    """User id
    """
    userId: int

    class Config:

        json_schema_extra = {
            "example": {
                'userId': 1,
                    }
                }


class UserIn(UserId):
    """User in
    """
    title: str
    body: str

    class Config:

        json_schema_extra = {
            "example": {
                'userId': 1,
                'title': 'some title',
                'body': 'some body',
                    }
                }


class Status(BaseModel):
    """Status of data processing
    """
    result: ProcessingResult = ProcessingResult.PROCESS

    class Config:

        json_schema_extra = {
            "example": {
                'result': 'inProcess',
                    }
                }


class Post(BaseModel):
    """Created placeholder resource
    """
    postId: int | None = None

    class Config:

        json_schema_extra = {
            "example": {
                'postId': 225,
                    }
                }


class UserOut(UserId, Status, Post):
    """Processed user
    """

    class Config:

        json_schema_extra = {
            "example": {
                'userId': 1,
                'result': 'error',
                'postId': None,
                    }
                }


class Data(BaseModel):
    """All data status
    """
    uuid_id: UUID4
    data_in: int = 0
    data_out: int = 0
    errors: int = 0
    result: ProcessingResult = ProcessingResult.PROCESS

    class Config:

        json_schema_extra = {
            "example": {
                'uuid_id': UUID_ID,
                'data_in': 12,
                'data_out': 0,
                'errors': 0,
                'result': 'progress',
                    }
                }


class DataOut(Data):
    """All data
    """
    data: dict[int, UserOut] = {}

    class Config:

        json_schema_extra = {
            "example": {
                'uuid_id': UUID_ID,
                'data_in': 12,
                'data_out': 0,
                'errors': 1,
                'result': 'progress',
                'data': {
                    1: {'userId': 1, 'result': 'error', 'postId': None,},
                        }
                    }
                }
