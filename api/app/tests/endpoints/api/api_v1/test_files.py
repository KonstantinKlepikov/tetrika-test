import pytest
import uuid
import random
from redis.asyncio import Redis
from typing import Callable
from httpx import AsyncClient
from app.config import settings
from app.core import uploades


rnd = random.Random()
rnd.seed(123)
UUID_ID = uuid.UUID(int=rnd.getrandbits(128), version=4)


class TestGetFile:
    """Test get file
    """

    async def test_get_file_returns_200(
        self,
        client: AsyncClient,
            ) -> None:
        """Test get file returns 200
        """
        response = await client.get(f"{settings.API_V1}/file")
        assert response.status_code == 200, f'{response.content=}'

class TestPostFile:
    """Test get file
    """
    @pytest.fixture(scope="function")
    async def mock_make_resources(
        self,
        monkeypatch,
            ) -> None:
        """Mock make resources
        """
        async def mock_return(*args, **kwargs) -> Callable:
            return None # TODO:

        monkeypatch.setattr(uploades, "make_resources", mock_return)

    @pytest.fixture(scope="function")
    async def mock_upload_file(
        self,
        monkeypatch,
            ) -> None:
        """Mock upload file
        """
        # TODO:

    @pytest.fixture(scope="function")
    def mock_uuid(
        self,
        monkeypatch,
            ) -> None:
        """Mock uuid
        """
        def mock_return(*args, **kwargs) -> Callable:
            return UUID_ID

        monkeypatch.setattr(uuid, "uuid4", mock_return)

    @pytest.fixture(scope="function")
    def csv_file(self, tmp_path) -> bytes:
        f = tmp_path / 'fileupload'
        with open(f, 'wb') as tmp:
            tmp.write(b'some file')
        with open(f, 'rb') as tmp:
            return tmp.read()

    async def test_post_file_returns_201(
        self,
        client: AsyncClient,
        csv_file: bytes,
        mock_uuid: Callable,
        mock_make_resources: Callable,
            ) -> None:
        """Test post file returns 201
        """
        response = await client.post(
            f"{settings.API_V1}/file",
            files={"file": ("myfile.csv", csv_file, 'text/csv')}
            )

        assert response.status_code == 201, f'{response.content=}'
        assert 'Wrong file format' not in response.text, f'{response.content=}'
        assert 'File sent' in response.text, f'{response.content=}'
        assert str(UUID_ID) in response.text, f'{response.content=}'

    async def test_post_file_if_frong_csv(
        self,
        client: AsyncClient,
        csv_file: bytes,
        mock_uuid: Callable,
        mock_make_resources: Callable,
            ) -> None:
        """Test post file return some txt if wrong csv
        """
        response = await client.post(
            f"{settings.API_V1}/file",
            files={"file": ("myfile.csv", csv_file, "image/jpeg")}
            )

        assert response.status_code == 201, f'{response.content=}'
        assert 'Wrong file format' in response.text, f'{response.content=}'
        assert 'File sent' not in response.text, f'{response.content=}'
        assert str(UUID_ID) not in response.text, f'{response.content=}'
