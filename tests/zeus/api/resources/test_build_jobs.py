# NOQA: flake8 is not happy about empty line here


def test_build_jobs_list(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/builds/{}/jobs'.format(default_repo.name, default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_job.id)


def test_build_jobs_list_empty(
    client, default_login, default_repo, default_build, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/builds/{}/jobs'.format(default_repo.name, default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
