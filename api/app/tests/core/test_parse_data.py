import pytest
from functools import lru_cache
from app.core.uploades import parse_data
from tests.conftest import UUID_ID


class TestParseData:
    """Test parse data function
    """

    @pytest.fixture(scope='function')
    @lru_cache
    def csv_data(self) -> str:
        """Get csv
        """
        with open('tests/test_file.csv') as f:
            return f.read()

    def test_parse_data_empty(self) -> None:
        """Test empty input
        """
        result = parse_data('', UUID_ID)
        assert isinstance(result[0], dict), 'wrong type of parsed data'
        assert result[0]["data_in"] == 0, 'wrong data_in'
        assert result[0]["errors"] == 0, 'wrong errors'
        assert isinstance(result[1], list), 'wrong type of processed data'

    def test_parse_data(self, csv_data: str) -> None:
        """Test parse nonempty data
        """
        result = parse_data(csv_data, UUID_ID)
        assert len(result[1]) == 3, 'wrong to process'
        assert result[0]["data_in"] == 4, 'wrong data_in'
        assert result[0]["errors"] == 1, 'wrong errors'
