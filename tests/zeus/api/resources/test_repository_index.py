from zeus import factories


def test_repo_list(client, default_login, default_repo, default_repo_access):
    resp = client.get('/api/repos')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_repo.id)


def test_repo_list_without_access(client, default_login, default_repo):
    resp = client.get('/api/repos')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_repo_list_excludes_public(client, default_login):
    factories.RepositoryFactory(public=True)
    resp = client.get('/api/repos')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
