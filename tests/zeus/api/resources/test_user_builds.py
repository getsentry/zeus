from zeus import factories


def test_user_build_list(client, default_login, default_repo, default_build, default_repo_access):
    author = factories.AuthorFactory(
        repository=default_repo,
        email=default_login.email,
    )
    build = factories.BuildFactory(
        repository=default_repo,
        author=author,
    )
    resp = client.get('/api/users/me/builds'.format(default_repo.name))
    assert resp.status_code == 200
    data = resp.json()
    # default_build should not be present due to author email
    assert len(data) == 1
    assert data[0]['id'] == str(build.id)
