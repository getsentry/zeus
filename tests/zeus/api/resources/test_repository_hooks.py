from zeus.models import Hook


def test_repo_hook_list(client, default_login, default_hook, default_repo, default_repo_access):
    resp = client.get('/api/repos/{}/{}/hooks'.format(default_repo.owner_name, default_repo.name))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_hook.id)
    assert data[0]['token']
    assert data[0]['base_uri']


def test_repo_hook_list_without_access(client, default_login, default_build, default_repo):
    resp = client.get('/api/repos/{}/{}/hooks'.format(default_repo.owner_name, default_repo.name))
    assert resp.status_code == 404


def test_repo_hook_create(client, default_login, default_source, default_repo, default_repo_access):
    resp = client.post(
        '/api/repos/{}/{}/hooks'.format(default_repo.owner_name, default_repo.name),
        json={
            'provider': 'travis-ci',
        }
    )
    assert resp.status_code == 200, repr(resp.data)

    hook = Hook.query.unrestricted_unsafe().get(resp.json()['id'])
    assert hook
    assert hook.repository_id == default_repo.id
    assert hook.provider == 'travis-ci'
    assert hook.token
