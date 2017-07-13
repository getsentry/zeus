from zeus.models import Repository, RepositoryAccess, RepositoryBackend


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


def test_new_repository(client, default_login, default_user):
    resp = client.post(
        '/api/repos', json={
            'url': 'https://github.com/getsentry/zeus.git',
            'backend': 'git',
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id']

    repo = Repository.query.unrestricted_unsafe().get(data['id'])
    assert repo.url == 'https://github.com/getsentry/zeus.git'
    assert repo.backend == RepositoryBackend.git

    access = list(RepositoryAccess.query.filter(RepositoryAccess.repository_id == repo.id))
    assert len(access) == 1
    assert access[0].user_id == default_user.id
