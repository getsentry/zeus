from zeus import factories


def test_build_tests_list(
    client, db_session, default_login, default_repo, default_build, default_repo_access
):
    job1 = factories.JobFactory(build=default_build)
    job2 = factories.JobFactory(build=default_build)
    db_session.add(job1)
    db_session.add(job2)

    testcase1 = factories.TestCaseFactory(job=job1, name="bar", passed=True)
    testcase2 = factories.TestCaseFactory(job=job2, name="foo", passed=True)
    testcase3 = factories.TestCaseFactory(job=job2, name="bar", failed=True)
    db_session.add(testcase1)
    db_session.add(testcase2)
    db_session.add(testcase3)

    resp = client.get(
        "/api/repos/{}/builds/{}/tests".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "bar"
    assert data[0]["result"] == "failed"
    assert (
        data[0]["runs"]
        == [
            {
                "id": str(testcase3.id),
                "job_id": str(job2.id),
                "result": "failed",
                "duration": testcase3.duration,
            },
            {
                "id": str(testcase1.id),
                "job_id": str(job1.id),
                "result": "passed",
                "duration": testcase1.duration,
            },
        ]
    )
    assert data[1]["name"] == "foo"
    assert data[1]["result"] == "passed"
    assert (
        data[1]["runs"]
        == [
            {
                "id": str(testcase2.id),
                "job_id": str(job2.id),
                "result": "passed",
                "duration": testcase2.duration,
            }
        ]
    )


def test_build_tests_list_empty(
    client, default_login, default_repo, default_build, default_repo_access
):
    resp = client.get(
        "/api/repos/{}/builds/{}/tests".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_build_tests_list_result_filter(
    client,
    default_login,
    default_repo,
    default_build,
    default_testcase,
    default_repo_access,
):
    resp = client.get(
        "/api/repos/{}/builds/{}/tests?result=failed".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0

    resp = client.get(
        "/api/repos/{}/builds/{}/tests?result=passed".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == default_testcase.name
