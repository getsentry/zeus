from zeus.models import Hook


def test_hook_details(client, default_login, default_hook, default_repo, default_repo_access):
    resp = client.get('/api/hooks/{}'.format(default_hook.id))
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_hook.id)


def test_cannot_load_hook_without_admin(
        client, default_login, default_hook, default_repo, default_repo_write_access):
    resp = client.get('/api/hooks/{}'.format(default_hook.id))
    assert resp.status_code == 400


def test_hook_delete(client, default_login, default_hook, default_repo, default_repo_access):
    resp = client.delete('/api/hooks/{}'.format(default_hook.id))
    assert resp.status_code == 204

    assert not Hook.query.get(default_hook.id)


def test_cannot_delete_hook_without_admin(
        client, default_login, default_hook, default_repo, default_repo_write_access):
    resp = client.delete('/api/hooks/{}'.format(default_hook.id))
    assert resp.status_code == 400


def test_hook_update(client, default_login, default_hook, default_repo, default_repo_access):
    resp = client.put(
        '/api/hooks/{}'.format(default_hook.id),
        json={
            'provider': 'travis',
            'config': {
                'domain': 'api.travis-ci.org',
            }
        }
    )
    assert resp.status_code == 200, repr(resp.data)

    hook = Hook.query.unrestricted_unsafe().get(resp.json()['id'])
    assert hook.repository_id == default_repo.id
    assert hook.provider == 'travis'
    assert hook.config == {
        'domain': 'api.travis-ci.org',
    }


def test_cannot_update_hook_without_admin(
        client, default_login, default_hook, default_repo, default_repo_write_access):
    resp = client.put('/api/hooks/{}'.format(default_hook.id))
    assert resp.status_code == 400


def test_hook_update_without_config(
        client, default_login, default_hook, default_repo, default_repo_access):
    resp = client.put(
        '/api/hooks/{}'.format(default_hook.id),
        json={
            'provider': 'travis',
        }
    )
    assert resp.status_code == 200, repr(resp.data)

    hook = Hook.query.unrestricted_unsafe().get(resp.json()['id'])
    assert hook.repository_id == default_repo.id
    assert hook.provider == 'travis'
    # we're ensuring that the config doesnt get overwritten by the defaults
    assert hook.config == {
        'domain': 'api.travis-ci.com',
    }
