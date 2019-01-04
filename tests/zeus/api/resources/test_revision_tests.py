from zeus import factories


def test_build_tests_list(
    client,
    db_session,
    default_login,
    default_repo,
    default_revision,
    default_build,
    default_repo_access,
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
        "/api/repos/{}/revisions/{}/tests".format(
            default_repo.get_full_name(), default_revision.sha
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_build_tests_list_empty(
    client,
    default_login,
    default_repo,
    default_build,
    default_revision,
    default_repo_access,
):
    resp = client.get(
        "/api/repos/{}/revisions/{}/tests".format(
            default_repo.get_full_name(), default_revision.sha
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
