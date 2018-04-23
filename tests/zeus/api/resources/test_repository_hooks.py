from zeus.models import Hook


def test_repo_hook_list(
    client, default_login, default_hook, default_repo, default_repo_access
):
    resp = client.get("/api/repos/{}/hooks".format(default_repo.get_full_name()))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(default_hook.id)
    assert data[0]["token"]
    assert data[0]["secret_uri"]
    assert data[0]["public_uri"]


def test_cannot_list_hooks_without_admin(
    client, default_login, default_repo, default_repo_write_access
):
    resp = client.get("/api/repos/{}/hooks".format(default_repo.get_full_name()))
    assert resp.status_code == 400


def test_repo_hook_list_without_access(
    client, default_login, default_build, default_repo
):
    resp = client.get("/api/repos/{}/hooks".format(default_repo.get_full_name()))
    assert resp.status_code == 404


def test_repo_hook_create(
    client, default_login, default_source, default_repo, default_repo_access
):
    resp = client.post(
        "/api/repos/{}/hooks".format(default_repo.get_full_name()),
        json={"provider": "travis"},
    )
    assert resp.status_code == 200, repr(resp.data)

    hook = Hook.query.unrestricted_unsafe().get(resp.json()["id"])
    assert hook
    assert hook.repository_id == default_repo.id
    assert hook.provider == "travis"
    assert hook.token


def test_cannot_create_hooks_without_admin(
    client, default_login, default_repo, default_repo_write_access
):
    resp = client.post(
        "/api/repos/{}/hooks".format(default_repo.get_full_name()),
        json={"provider": "travis"},
    )
    assert resp.status_code == 400


def test_repo_hook_create_custom_schema(
    client, default_login, default_source, default_repo, default_repo_access
):
    resp = client.post(
        "/api/repos/{}/hooks".format(default_repo.get_full_name()),
        json={"provider": "custom"},
    )
    assert resp.status_code == 200, repr(resp.data)

    hook = Hook.query.unrestricted_unsafe().get(resp.json()["id"])
    assert hook
    assert hook.repository_id == default_repo.id
    assert hook.provider == "custom"
    assert hook.token
    assert hook.config == {}


def test_repo_hook_create_travis_schema(
    client, default_login, default_source, default_repo, default_repo_access
):
    resp = client.post(
        "/api/repos/{}/hooks".format(default_repo.get_full_name()),
        json={"provider": "travis", "config": {"domain": "api.travis-ci.org"}},
    )
    assert resp.status_code == 200, repr(resp.data)

    hook = Hook.query.unrestricted_unsafe().get(resp.json()["id"])
    assert hook
    assert hook.repository_id == default_repo.id
    assert hook.provider == "travis"
    assert hook.token
    assert hook.config == {"domain": "api.travis-ci.org"}
