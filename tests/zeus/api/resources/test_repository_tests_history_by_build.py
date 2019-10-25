def test_repository_tests_history_by_build(
    client,
    default_login,
    default_build,
    default_testcase,
    default_repo,
    default_repo_access,
):
    resp = client.get(
        "/api/repos/{}/tests-by-build".format(
            default_repo.get_full_name(), default_testcase.hash
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == {default_testcase.name: ["passed"]}
    assert len(data["builds"]) == 1
    assert data["builds"][0]["id"] == str(default_build.id)
