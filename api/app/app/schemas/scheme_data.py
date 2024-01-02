from pydantic import BaseModel, Field
from app.schemas.constraint import ProcessingResult


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
    result: ProcessingResult = Field(
        default=ProcessingResult.PROCESS, validate_default=True
            )

    class Config:

        use_enum_values = True
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

        use_enum_values = True
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
    data_in: int = 0
    data_out: int = 0
    errors: int = 0
    result: ProcessingResult = Field(
        default=ProcessingResult.PROCESS, validate_default=True
            )

    class Config:

        use_enum_values = True
        json_schema_extra = {
            "example": {
                'data_in': 12,
                'data_out': 0,
                'errors': 0,
                'result': 'progress',
                    }
                }


class DataOut(Data):
    """All data
    """

    class Config:

        use_enum_values = True
        extra = 'allow'
        json_schema_extra = {
            "example": {
                'data_in': 12,
                'data_out': 1,
                'errors': 1,
                'result': 'progress',
                1: '',
                    }
                }
