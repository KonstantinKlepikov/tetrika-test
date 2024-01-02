import toml
from typing import Type
from pydantic_settings import BaseSettings
from app.schemas import scheme_error


poetry_data = toml.load('pyproject.toml')['tool']['poetry']
ErrorType = dict[int, dict[str, Type[scheme_error.HttpErrorMessage]]]


class Settings(BaseSettings):
    # api vars
    API_V1: str = "/api/v1"

    # redis
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_HOST: str | None = None

    # aiohhtp client
    SIZE_POOL_HTTP: int = 100
    TIMEOUT_AIOHTTP: int = 2
    SEMAPHORE: int = 7

    # request external
    PL_URL: str = 'https://jsonplaceholder.typicode.com/posts'

    # open-api settings
    title: str = poetry_data['name']
    descriprion: str = poetry_data['description']
    version: str = poetry_data['version']
    openapi_tags: list = [
        {
            "name": "files",
            "description": "Files api",
        },
    ]

    # open-api errors
    ERRORS: ErrorType = {
        400: {'model': scheme_error.HttpError400},
        404: {'model': scheme_error.HttpError404},
        409: {'model': scheme_error.HttpError409},
            }


settings = Settings()
