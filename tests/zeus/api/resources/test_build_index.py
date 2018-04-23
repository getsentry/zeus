from zeus import factories


def test_build_list(client, default_login, default_build, default_repo_access):
    resp = client.get("/api/builds")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(default_build.id)


def test_build_list_without_access(client, default_login, default_build):
    resp = client.get("/api/builds")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_build_list_excludes_public(client, default_login):
    repo = factories.RepositoryFactory(public=True)
    factories.BuildFactory(repository=repo)
    resp = client.get("/api/builds")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
