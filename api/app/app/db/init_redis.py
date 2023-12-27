from typing import Generator, Any
from redis.asyncio import Redis
from fastapi.logger import logger as flog
from app.config import settings


class RedisConnection:
    def __init__(
        self, host: str = settings.REDIS_HOST,
        port: int = settings.REDIS_PORT,
        db: int = settings.REDIS_DB
            ) -> None:
        self.db = Redis(host=host, port=port, db=db)

    async def __aenter__(self) -> "Redis[Any]":
        return self.db

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.db.close()


async def get_redis_connection() -> Generator[Redis, None, None]:
    """Get redis session
    """
    async with RedisConnection() as db:
        flog.info("Create redis session")
        yield db
