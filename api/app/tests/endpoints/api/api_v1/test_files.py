import pytest
from httpx import AsyncClient
from app.config import settings
from tests.conftest import UUID_ID


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

    @pytest.fixture(scope="function")
    async def mock_upload_file(
        self,
        monkeypatch,
            ) -> None:
        """Mock upload file
        """
        # TODO: mocke me

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
