from zeus import factories


def test_repository_tests_history_by_build(
    client,
    default_login,
    default_build,
    default_testcase,
    default_repo,
    default_repo_access,
    default_source,
):
    other_build = factories.BuildFactory(source=default_source, finished=True)
    other_job = factories.JobFactory(build=other_build)
    factories.TestCaseFactory(job=other_job, name=default_testcase.name, failed=True)

    resp = client.get(
        "/api/repos/{}/tests-by-build".format(
            default_repo.get_full_name(), default_testcase.hash
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == {default_testcase.name: ["failed", "passed"]}
    assert len(data["builds"]) == 2
    assert data["builds"][0]["id"] == str(other_build.id)
    assert data["builds"][1]["id"] == str(default_build.id)
