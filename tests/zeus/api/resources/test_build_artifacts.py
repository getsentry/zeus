def test_build_artifacts_list(
    client,
    default_login,
    default_repo,
    default_build,
    default_job,
    default_artifact,
    default_repo_access,
):
    resp = client.get(
        "/api/repos/{}/builds/{}/artifacts".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(default_artifact.id)


def test_build_artifacts_list_empty(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    resp = client.get(
        "/api/repos/{}/builds/{}/artifacts".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
