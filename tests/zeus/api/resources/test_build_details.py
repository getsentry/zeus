def test_build_details(client, default_login, default_build, default_repo_access):
    resp = client.get('/api/builds/{}'.format(default_build.id))
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_build.id)
