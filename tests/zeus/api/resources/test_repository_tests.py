from zeus import factories


def test_repository_tests(
    client,
    default_login,
    default_build,
    default_job,
    default_testcase,
    default_repo,
    default_repo_access,
    default_revision,
):
    build2 = factories.BuildFactory(revision=default_revision, failed=True)
    job2 = factories.JobFactory(build=build2, failed=True)
    testcase1 = factories.TestCaseFactory(
        job=job2, name=default_testcase.name, failed=True
    )

    build3 = factories.BuildFactory(revision=default_revision, finished=True)
    job3 = factories.JobFactory(build=build3, passed=True)
    testcase2 = factories.TestCaseFactory(
        job=job3, passed=True, name=default_testcase.name + "2"
    )

    build4 = factories.BuildFactory(revision=default_revision, finished=True)
    job4 = factories.JobFactory(build=build4, passed=True)
    testcase3 = factories.TestCaseFactory(
        job=job4, name=default_testcase.name, passed=True
    )

    assert testcase2.hash != testcase1.hash

    resp = client.get("/api/repos/{}/tests".format(default_repo.get_full_name()))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0] == {
        "name": default_testcase.name,
        "hash": default_testcase.hash,
        "runs_failed": 1,
        "runs_total": 3,
        "avg_duration": int(
            (default_testcase.duration + testcase1.duration + testcase3.duration) / 3
        ),
    }
    assert data[1] == {
        "name": testcase2.name,
        "hash": testcase2.hash,
        "runs_failed": 0,
        "runs_total": 1,
        "avg_duration": testcase2.duration,
    }
