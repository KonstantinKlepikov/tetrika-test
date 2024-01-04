from typing import Any
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from app.schemas.scheme_data import UserIn
from app.util.blocker import Blocker
from app.config import settings


class SessionMaker:
    """Aiohttp client
    # TODO: test me
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
    async def post(
        cls,
        url: str,
        data: UserIn | None = None
            ) -> dict[str, Any]:
        """Request and get responses

        Args:
            url (str): url for request
            data (UserIn, optional): request body.
                Defaults to None.

        Returns:
            dict[str, Any]: response
        """
        client = cls.get_aiohttp_client()
        if data:
            data = data.model_dump()
        async with client.post(url, data=data) as response:
            if response.status == 429:
                raise ConnectionRefusedError
            return await response.json()
