import asyncio
from asyncio import Semaphore, Queue, Task
from datetime import datetime
from typing import Any
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from fastapi import HTTPException
from app.config import settings


class SessionMaker:
    """This class represents aiohttp client session singleton pattern
    """
    aiohttp_client: ClientSession | None = None
    queue: Queue = Queue()
    sem: Semaphore = Semaphore(settings.SEMAPHORE)
    dt_start: datetime | None = None
    workers: list[Task] | None = None

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
                # headers=headers,
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
    async def _get(
        cls,
        client: ClientSession,
        url: str,
        params: dict[str, Any] | None = None,
            ) -> dict[str, Any]:
        """Request and get responses

        Args:
            client (ClientSession): session
            url (str): url for request
            params (dict[str, Any], optional): request parameters.
                Defaults to None.

        Raises:
            HTTPException: response code depended exceptions

        Returns:
            dict[str, Any]: response
        """
        async with client.get(url, params=params) as response:
            if response.status == 429:
                raise HTTPException(
                    status_code=429,
                    detail="To Many Requests"
                        )
            return await response.json()


    async def worker(self) -> None:
        """Work with querie"""

        while True:

            job = await self.queue.get()

            async with self.sem:

                if self.sem._value == settings.SEMAPHORE+1:
                    self.dt_start = datetime.utcnow()

                if self.sem._value == 0:
                    timeout = 1 - (datetime.utcnow() - self.dt_start).total_seconds()
                    if timeout > 0:
                        await asyncio.sleep(timeout)
                        if self.sem.locked():
                            self.sem.release()

            await job()
            self.queue.task_done()


    async def run_workers(self) -> None:
        """Run workers
        """
        self.get_aiohttp_client()
        self.workers = [
            asyncio.create_task(self.worker())
            for _
            in range(settings.WORKERS)
                ]
        asyncio.wait(*self.workers)


    # async def stop_workers(self) -> None:
    #     """Stop workers
    #     """
    #     await self.queue.join()
    #     for worker in self.workers:
    #         worker.cancel()
    #     await self.close_aiohttp_client()
