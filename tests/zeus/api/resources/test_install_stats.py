from zeus import factories


def test_builds_total(client, default_login, default_repo, default_revision):
    factories.BuildFactory(revision=default_revision, passed=True)

    resp = client.get("/api/install/stats?points=30&resolution=1d&stat=builds.total")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 30
    for item in data[1:]:
        assert item["value"] == 0
    assert data[0]["value"] == 1


def test_builds_errored(client, default_login, default_repo, default_revision):
    factories.BuildFactory(revision=default_revision, errored=True)

    resp = client.get("/api/install/stats?points=30&resolution=1d&stat=builds.errored")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 30
    for item in data[1:]:
        assert item["value"] == 0
    assert data[0]["value"] == 1


def test_users_active(client, default_login, default_user):
    resp = client.get("/api/install/stats?points=30&resolution=1d&stat=users.active")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 30
    for item in data[1:]:
        assert item["value"] == 0
    assert data[0]["value"] == 1


def test_users_created(client, default_login, default_user):
    resp = client.get("/api/install/stats?points=30&resolution=1d&stat=users.created")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 30
    for item in data[1:]:
        assert item["value"] == 0
    assert data[0]["value"] == 1
