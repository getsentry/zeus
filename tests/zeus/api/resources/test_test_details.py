from zeus import factories


def test_test_details(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    testcase = factories.TestCaseFactory(
        job=default_job,
        failed=True,
    )
    resp = client.get(
        '/api/repos/{}/builds/{}/tests/{}'.
        format(default_repo.name, default_build.number, testcase.name)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(testcase.id)
    assert data['message'] == str(testcase.message)
