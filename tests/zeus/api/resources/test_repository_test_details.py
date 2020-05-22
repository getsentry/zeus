def test_repository_test_details(
    client,
    default_login,
    default_testcase,
    default_build,
    default_repo,
    default_repo_access,
):
    resp = client.get(
        "/api/repos/{}/tests/{}".format(
            default_repo.get_full_name(), default_testcase.hash
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["hash"] == str(default_testcase.hash)
    assert data["name"] == default_testcase.name
    assert data["first_build"]["id"] == str(default_build.id)
    assert data["last_build"]["id"] == str(default_build.id)
