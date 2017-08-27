# flake8 is breaking with no empty lines up here NOQA


def test_build_tests_list(
    client, default_login, default_repo, default_build, default_testcase, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/builds/{}/tests'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_testcase.id)


def test_build_tests_list_empty(
    client, default_login, default_repo, default_build, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/builds/{}/tests'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_build_tests_list_result_filter(
    client, default_login, default_repo, default_build, default_testcase, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/builds/{}/tests?result=failed'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0

    resp = client.get(
        '/api/repos/{}/builds/{}/tests?result=passed'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_testcase.id)
