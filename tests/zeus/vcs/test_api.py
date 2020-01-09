import pytest


@pytest.fixture(scope="function")
def client(loop, vcs_app, aiohttp_client):
    return loop.run_until_complete(aiohttp_client(vcs_app))


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/healthz")
    assert resp.status == 200
    assert await resp.text() == {"ok": true}
    # assert client.server.app["value"] == "foo"
