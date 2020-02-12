import pytest

from uuid import UUID, uuid4

from zeus.vcs.server import build_app


@pytest.fixture(scope="function")
async def vcs_app(loop):
    app = await build_app(loop=loop)
    return app


@pytest.fixture(scope="function", autouse=True)
async def asyncdb_transaction(loop, request, vcs_app):
    tr = await vcs_app["db"].transaction()
    await tr.start()
    try:
        yield
    finally:
        await tr.rollback()


@pytest.fixture(scope="function")
async def default_repo_id(vcs_app) -> UUID:
    rv = await vcs_app["db"].fetch(
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
