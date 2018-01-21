from zeus.models import Repository


def test_repo_details(client, default_login, default_repo, default_repo_access):
    resp = client.get('/api/repos/{}'.format(default_repo.get_full_name()))
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_repo.id)


def test_update_cannot_change_provider(client, default_login, default_repo, default_repo_access):
    resp = client.put('/api/repos/{}'.format(default_repo.get_full_name()), json={
        'provider': 'git',
    })
    assert resp.status_code == 200
    repo = Repository.query.unrestricted_unsafe().get(default_repo.id)
    assert repo.provider.name == 'github'


def test_update_change_public(client, default_login, default_repo, default_repo_access):
    resp = client.put('/api/repos/{}'.format(default_repo.get_full_name()), json={
        'public': True,
    })
    assert resp.status_code == 200
    repo = Repository.query.unrestricted_unsafe().get(default_repo.id)
    assert repo.public

    resp = client.put('/api/repos/{}'.format(default_repo.get_full_name()), json={
        'public': False,
    })
    assert resp.status_code == 200
    repo = Repository.query.unrestricted_unsafe().get(default_repo.id)
    assert not repo.public


def test_cannot_update_without_admin(
        client, default_login, default_repo, default_repo_write_access):
    resp = client.put('/api/repos/{}'.format(default_repo.get_full_name()), json={
        'public': True,
    })
    assert resp.status_code == 400
