def test_repository_test_history(
    client,
    default_login,
    default_build,
    default_testcase,
    default_repo,
    default_repo_access,
):
    resp = client.get(
        "/api/repos/{}/tests/{}/history".format(
            default_repo.get_full_name(), default_testcase.hash
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["hash"] == str(default_testcase.hash)
    assert data[0]["build"]["id"] == str(default_build.id)
