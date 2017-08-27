def test_repo_details(client, default_login, default_repo, default_repo_access):
    resp = client.get('/api/repos/{}'.format(default_repo.get_full_name()))
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_repo.id)
