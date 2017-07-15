from zeus import factories


def test_user_build_list(
    client, default_login, default_org, default_project, default_build, default_repo_access,
    default_revision
):
    author = factories.AuthorFactory(
        organization=default_org,
        email=default_login.email,
    )
    source = factories.SourceFactory(
        revision=default_revision,
        author=author,
    )
    build = factories.BuildFactory(
        project=default_project,
        source=source,
    )
    resp = client.get('/api/users/me/builds')
    assert resp.status_code == 200
    data = resp.json()
    # default_build should not be present due to author email
    assert len(data) == 1
    assert data[0]['id'] == str(build.id)
