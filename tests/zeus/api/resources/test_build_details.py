def test_build_details(client, default_login, default_repo, default_build, default_repo_access):
    resp = client.get(
        '/api/repos/{}/{}/builds/{}'.
        format(default_repo.owner_name, default_repo.name, default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_build.id)
