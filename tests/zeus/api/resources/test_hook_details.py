from zeus.models import Hook


def test_hook_details(client, default_login, default_hook, default_repo, default_repo_access):
    resp = client.get('/api/hooks/{}'.format(default_hook.id))
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_hook.id)


def test_hook_delete(client, default_login, default_hook, default_repo, default_repo_access):
    resp = client.delete('/api/hooks/{}'.format(default_hook.id))
    assert resp.status_code == 204

    assert not Hook.query.get(default_hook.id)
