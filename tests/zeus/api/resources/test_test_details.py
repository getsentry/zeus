from zeus import factories


def test_test_details(
    client, default_login, default_org, default_project, default_build, default_job,
    default_repo_access
):
    testcase = factories.TestCaseFactory(
        job=default_job,
        failed=True,
    )
    resp = client.get(
        '/api/projects/{}/{}/builds/{}/tests/{}'.
        format(default_org.name, default_project.name, default_build.number, testcase.name)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(testcase.id)
    assert data['message'] == str(testcase.message)
