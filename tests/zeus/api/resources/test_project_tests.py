# NOQA


def test_project_test_list(
    client, default_login, default_org, default_project, default_build, default_testcase,
    default_repo_access
):
    resp = client.get('/api/projects/{}/{}/tests'.format(default_org.name, default_project.name))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_testcase.id)
