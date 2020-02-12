import pytest

from uuid import UUID

from zeus import auth


class ApiHelper(object):
    def __init__(self, client):
        self.client = client

    def get(self, path: str, repo_id: UUID, **params):
        if "tenant" not in params:
            tenant = auth.RepositoryTenant(repository_id=repo_id)
        else:
            tenant = params.pop("tenant", None)

        headers = {}
        if tenant:
            headers["Authorization"] = "token {}".format(
                auth.generate_token(tenant).decode("utf-8")
            )

        return self.client.get(
            f"{path}?repo_id={repo_id}&{'&'.join('{}={}'.format(k, v) for k, v in params.items())}",
            headers=headers,
        )


@pytest.fixture(scope="function")
def client(loop, vcs_app, aiohttp_client):
    return loop.run_until_complete(aiohttp_client(vcs_app))


async def test_health_check(client):
    resp = await client.get("/healthz")
    assert resp.status == 200, resp.content
    assert await resp.text() == '{"ok": true}'


async def test_log_unauthorized(client, default_repo_id):
    resp = await ApiHelper(client).get(
        "/stmt/log", repo_id=default_repo_id, tenant=None
    )
    assert resp.status == 401, resp.content


async def test_log_basic(client, default_repo_id):
    resp = await ApiHelper(client).get("/stmt/log", repo_id=default_repo_id)
    assert resp.status == 200, resp.content
    data = await resp.json()
    assert data["log"], data


async def test_branches_basic(client, default_repo_id):
    resp = await ApiHelper(client).get("/stmt/branches", repo_id=default_repo_id)
    assert resp.status == 200, resp.content
    data = await resp.json()
    assert data["branches"], data


async def test_branches_show(client, default_repo_id):
    resp = await ApiHelper(client).get(
        "/stmt/show", repo_id=default_repo_id, sha="HEAD", filename="README.md"
    )
    assert resp.status == 200, resp.content
    data = await resp.json()
    assert data["show"], data


async def test_branches_export(client, default_repo_id):
    resp = await ApiHelper(client).get(
        "/stmt/export", repo_id=default_repo_id, sha="HEAD", filename="README.md"
    )
    assert resp.status == 200, resp.content
    data = await resp.json()
    assert data["export"], data
