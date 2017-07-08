def test_job_details(client, default_login, default_job, default_repo_access):
    resp = client.get('/api/jobs/{}'.format(default_job.id))
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_job.id)
