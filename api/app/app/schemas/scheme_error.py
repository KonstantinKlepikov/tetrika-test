from pydantic import BaseModel


class HttpErrorMessage(BaseModel):
    """Http error
    """
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Some information about error.",
            }
        }


class HttpError400(HttpErrorMessage):
    """400 Bad Request
    """

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Wrong file or problems with connection.",
                }
            }


class HttpError404(HttpErrorMessage):
    """404 Not Found
    """

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Resource not found.",
            }
        }


class HttpError409(HttpErrorMessage):
    """409 Conflict
    """

    class Config:
        json_schema_extra = {
            "example": {
                "detail":
                    "Something wrong with client or server data.",
                }
            }
