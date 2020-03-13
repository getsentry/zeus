import pytest

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID

from zeus import auth
from zeus.exceptions import UnknownRevision
from zeus.vcs.backends.git import RevisionResult


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
            headers["Authorization"] = "Bearer zeus-t-{}".format(
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


async def test_log_fetches_on_retry(client, mocker, default_repo_id):
    vcs_log = mocker.patch(
        "zeus.vcs.backends.git.GitVcs.log",
        AsyncMock(
            side_effect=[
                UnknownRevision("master"),
                [
                    RevisionResult(
                        sha="c" * 40,
                        author="Foo Bar <foo@example.com>",
                        committer="Biz Baz <baz@example.com>",
                        author_date=datetime(2013, 9, 19, 22, 15, 22),
                        committer_date=datetime(2013, 9, 19, 22, 15, 23),
                        message="Hello world!",
                    )
                ],
            ]
        ),
    )

    resp = await ApiHelper(client).get("/stmt/log", repo_id=default_repo_id)
    assert resp.status == 200, resp.content
    data = await resp.json()
    assert len(data["log"]) == 1
    assert data["log"][0]["sha"] == "c" * 40

    vcs_log.assert_has_calls(
        [
            mocker.call(branch=None, limit=100, offset=0, parent=None),
            mocker.call(
                branch=None, limit=100, offset=0, parent=None, update_if_exists=True
            ),
        ]
    )


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
