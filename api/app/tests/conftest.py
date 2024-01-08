import pytest
import uuid
import random
from redis.asyncio import Redis
from typing import AsyncGenerator
from pydantic_settings import BaseSettings
from httpx import AsyncClient
from app.main import app
from app.db import init_redis
from app.db.init_redis import RedisConnection
from app.schemas.scheme_data import UsersStatus


rnd = random.Random()
rnd.seed(123)
UUID_ID = uuid.UUID(int=rnd.getrandbits(128), version=4)


async def override_uuid_id():
    return UUID_ID


class TestSettings(BaseSettings):
    """Test settings"""
    TEST_REDIS_PORT: int = 6379
    TEST_REDIS_DB: int = 0
    TEST_REDIS_HOST: str | None = 0


test_settings = TestSettings()


async def get_test_redis_connection() -> AsyncGenerator[Redis, None]:
    """Get redis session
    """
    async with RedisConnection(
        host=test_settings.TEST_REDIS_HOST,
        port=test_settings.TEST_REDIS_PORT,
        db=test_settings.TEST_REDIS_DB,
            ) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[Redis, None]:
    """Get redis client
    """
    async with RedisConnection(
        host=test_settings.TEST_REDIS_HOST,
        port=test_settings.TEST_REDIS_PORT,
        db=test_settings.TEST_REDIS_DB
            ) as db:
        await db.flushdb()
        await db.hmset(
            str(UUID_ID),
            UsersStatus.Config.json_schema_extra['example']
                )
        yield db
        await db.flushdb()


@pytest.fixture(scope="function")
async def client(db) -> AsyncClient:
    """Get api client
    """
    app.dependency_overrides[uuid.uuid4] = override_uuid_id
    app.dependency_overrides[
        init_redis.get_redis_connection
            ] = get_test_redis_connection
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    app.dependency_overrides = {}
