import asyncio
import time
from typing import Any, Callable
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from fastapi.logger import logger as fastapi_logger
from app.schemas.scheme_data import UserIn
from app.config import settings


class Blocker:
    """Block request after limit requests per period (in seconds)
    """

    def __init__(
        self,
        limit: int = settings.SEMAPHORE,
        period: float = 1.0
            ) -> None:
        self.limit = limit
        self.period = period
        self._sem: asyncio.Semaphore = asyncio.Semaphore(limit)
        self._finaly: list[float] = []

    async def sleep(self) -> None:
        """Sleep if time is gone
        # TODO: test me
        """
        if len(self._finaly) >= self.limit:
            sleep_before = self._finaly.pop(0)
            fastapi_logger.debug(f'{sleep_before=}')

            if sleep_before >= time.monotonic():
                await asyncio.sleep(sleep_before - time.monotonic())
                fastapi_logger.debug('Sleep')

    def __call__(self, func: Callable) -> Callable:
        """Decorator protocol
        # TODO: test me
        """
        async def wrapper(*args, **kwargs):

            async with self._sem:
                fastapi_logger.debug(f'Sem value {self._sem._value}')

                await self.sleep()
                res = await func(*args, **kwargs)
                self._finaly.append(time.monotonic() + self.period)

            return res

        return wrapper


class SessionMaker:
    """Aiohttp client
    """
    aiohttp_client: ClientSession | None = None
    blocker: Blocker = Blocker()

    @classmethod
    def get_aiohttp_client(cls) -> ClientSession:
        """Get aiohttp client session

        Returns:
            ClientSession: client session object
        """
        if cls.aiohttp_client is None:
            timeout = ClientTimeout(total=settings.TIMEOUT_AIOHTTP)
            connector = TCPConnector(
                limit_per_host=settings.SIZE_POOL_HTTP
                    )
            cls.aiohttp_client = ClientSession(
                timeout=timeout,
                connector=connector,
                    )

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        """Close aiohttp session
        """
        if cls.aiohttp_client:
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @classmethod
    @blocker
    async def post_user(self, url: str, data: UserIn) -> dict[str, Any]:
        """Request and get responses

        Args:
            url (str): url for request
            data (UserIn): request body.

        Returns:
            dict[str, Any]: response
        # TODO: test me
        """
        client = self.get_aiohttp_client()
        async with client.post(url, data=data.model_dump()) as response:
            if response.status == 429:
                raise ConnectionRefusedError
            return await response.json()
