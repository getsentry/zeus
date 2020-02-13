import pytest

from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from zeus.vcs.server import build_app


class FakePool:
    def __init__(self, pool):
        self.pool = pool
        self.conn = None

    @asynccontextmanager
    async def acquire(self):
        if self.conn is None:
            ctx = self.pool.acquire()
            self.conn = await ctx.__aenter__()
        yield self.conn


@pytest.fixture(scope="function")
async def vcs_app(loop, req_ctx):
    app = await build_app(loop=loop)
    app["db_pool"] = FakePool(app["db_pool"])
    return app


@pytest.fixture(scope="function")
async def vcs_db_pool(vcs_app):
    return vcs_app["db_pool"]


@pytest.fixture(scope="function", autouse=True)
async def vcs_db(mocker, loop, request, vcs_db_pool):
    async with vcs_db_pool.acquire() as conn:
        tr = conn.transaction()
        await tr.start()
        try:
            yield conn
        finally:
            await tr.rollback()


@pytest.fixture(scope="function")
async def default_repo_id(vcs_db) -> UUID:
    rv = await vcs_db.fetch(
        """
        INSERT INTO repository (id, owner_name, name, url, provider, backend, status, external_id)
        VALUES ($1::uuid, $2, $3, $4, $5, $6, $7, $8)
        RETURNING ID
    """,
        str(uuid4()),
        "getsentry",
        "zeus",
        "https://github.com/getsentry/zeus.git",
        "github",
        1,
        1,
        "1",
    )
    return rv[0]["id"]
