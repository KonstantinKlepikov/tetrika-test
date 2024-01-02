from typing import Any
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from fastapi import HTTPException
from app.config import settings


class SessionMaker:
    """This class represents aiohttp client session singleton pattern
    """
    aiohttp_client: ClientSession | None = None

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
    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
            ) -> dict[str, Any]:
        """Request and get responses

        Args:
            url (str): url for request
            data (dict[str, Any], optional): request body.
                Defaults to None.

        Raises:
            HTTPException: response code depended exceptions

        Returns:
            dict[str, Any]: response
        """
        client = self.get_aiohttp_client()
        async with client.post(url, data=data) as response:
            if response.status == 429:
                raise HTTPException(
                    status_code=429,
                    detail="To Many Requests"
                        )
            return await response.json()
