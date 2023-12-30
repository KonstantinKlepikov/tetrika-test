import pytest
import uuid
import random
from typing import Generator
from pydantic_settings import BaseSettings
from httpx import AsyncClient
from app.main import app
from app.db.init_redis import RedisConnection


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


@pytest.fixture(scope="function")
async def client() -> Generator:
    """Get api client
    """
    app.dependency_overrides[uuid.uuid4] = override_uuid_id
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
async def redis_db() -> Generator:
    """Get redis client
    """
    async with RedisConnection(
        host=test_settings.TEST_REDIS_HOST,
        port=test_settings.TEST_REDIS_PORT,
        db=test_settings.TEST_REDIS_DB
            ) as db:
        db.flushdb()
        yield db
        db.flushdb()
