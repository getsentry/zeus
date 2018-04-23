from zeus import factories


def test_user_build_list(
    client,
    default_login,
    default_build,
    default_repo,
    default_repo_access,
    default_revision,
):
    factories.BuildFactory(repository=default_repo)

    resp = client.get("/api/users/me/builds".format(default_repo.name))
    assert resp.status_code == 200
    data = resp.json()
    # newly created build should not be present due to author email
    assert len(data) == 1
    assert data[0]["id"] == str(default_build.id)
