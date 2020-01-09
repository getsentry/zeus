import pytest

from uuid import uuid4

from zeus.vcs.server import build_app


@pytest.fixture(scope="function")
async def vcs_app():
    app = await build_app()
    return app


@pytest.fixture(scope="function", autouse=True)
async def asyncdb_transaction(request, vcs_app):
    has_marker = request.node.get_closest_marker("asyncio")
    if has_marker:
        tr = await vcs_app["db"].transaction()
        await tr.start()
        try:
            yield
        except Exception:
            await tr.rollback()
            raise
        else:
            await tr.commit()
    else:
        yield


@pytest.fixture(scope="function")
async def default_repo(vcs_app):
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
    return rv[0]
