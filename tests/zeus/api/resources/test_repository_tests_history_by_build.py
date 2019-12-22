from zeus import factories


def test_repository_tests_history_by_build(
    client,
    default_login,
    default_build,
    default_testcase,
    default_repo,
    default_repo_access,
    default_revision,
):
    build2 = factories.BuildFactory(revision=default_revision, finished=True)
    job2 = factories.JobFactory(build=build2)
    factories.TestCaseFactory(job=job2, name=default_testcase.name, failed=True)

    build3 = factories.BuildFactory(revision=default_revision, finished=True)
    job3 = factories.JobFactory(build=build3)
    testcase2 = factories.TestCaseFactory(
        job=job3, passed=True, name=default_testcase.name + "2"
    )

    build4 = factories.BuildFactory(revision=default_revision, finished=True)
    job4 = factories.JobFactory(build=build4)
    factories.TestCaseFactory(job=job4, name=default_testcase.name, passed=True)

    resp = client.get(
        "/api/repos/{}/tests-by-build?results=3".format(
            default_repo.get_full_name(), default_testcase.hash
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tests"] == [
        {
            "name": default_testcase.name,
            "hash": default_testcase.hash,
            "results": ["passed", None, "failed"],
        },
        {
            "name": testcase2.name,
            "hash": testcase2.hash,
            "results": [None, "passed", None],
        },
    ]
    assert len(data["builds"]) == 3
    assert data["builds"][0]["id"] == str(build4.id)
    assert data["builds"][1]["id"] == str(build3.id)
    assert data["builds"][2]["id"] == str(build2.id)
