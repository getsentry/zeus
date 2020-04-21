import asyncio
import pytest

from time import time
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

from zeus.vcs.server import cleanup_scheduler


async def test_cleanup_scheduler(mocker, vcs_db_pool, default_repo_id: UUID):
    async def update_last_run(conn, repo_id):
        assert repo_id == default_repo_id
        await conn.fetch(
            """INSERT INTO itemoption (id, item_id, name, value)
    VALUES ($1::uuid, $2, $3, $4)
    ON CONFLICT DO NOTHING
    RETURNING id;""",
            str(uuid4()),
            default_repo_id,
            "cleanup.last-run",
            str(time()),
        )

    mock_cleanup = mocker.patch(
        "zeus.vcs.server.cleanup", AsyncMock(side_effect=update_last_run)
    )

    queue = asyncio.Queue()

    future = asyncio.ensure_future(cleanup_scheduler(vcs_db_pool, queue))

    await asyncio.sleep(1)

    mock_cleanup.assert_called_once()

    with pytest.raises(asyncio.CancelledError):
        future.cancel()
        await future
