import pytest

from datetime import datetime, timezone
from unittest.mock import patch

pytest_plugins = ["zeus.testutils.pytest", "zeus.testutils.fixtures"]


@pytest.fixture(scope="session", autouse=True)
def mock_datetime():
    fixed_now = datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    cm = patch("zeus.utils.timezone.now", return_value=fixed_now)
    cm.__enter__()
