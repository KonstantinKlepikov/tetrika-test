import asyncio
import time
from fastapi.logger import logger as fastapi_logger
from app.config import settings


class Blocker:
    """Block request after limit requests per period (in seconds)
    """

    def __init__(self, limit: int = settings.SEMAPHORE, period: float = 1.0):
        self.limit = limit
        self.period = period
        self._sem: asyncio.Semaphore = asyncio.Semaphore(limit)
        self._finaly: list[float] = []

    async def sleep(self):
        """Sleep if time is gone
        # TODO: test me
        """
        if len(self._finaly) >= self.limit:
            sleep_before = self._finaly.pop(0)
            fastapi_logger.debug(f'{sleep_before=}')

            if sleep_before >= time.monotonic():
                await asyncio.sleep(sleep_before - time.monotonic())
                fastapi_logger.debug('Sleep')

    def __call__(self, func):
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
