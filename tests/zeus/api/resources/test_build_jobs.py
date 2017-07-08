def test_build_jobs_list(client, default_login, default_build, default_job, default_repo_access):
    resp = client.get('/api/builds/{}/jobs'.format(default_build.id))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_job.id)


def test_build_jobs_list_empty(client, default_login, default_build, default_repo_access):
    resp = client.get('/api/builds/{}/jobs'.format(default_build.id))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
