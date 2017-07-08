import json

from zeus.testutils import assert_json_response


def test_build_jobs_list(client, default_login, default_build, default_job, default_repo_access):
    resp = client.get('/api/builds/{}/jobs'.format(default_build.id))
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]['id'] == str(default_job.id)


def test_build_jobs_list_empty(client, default_login, default_build, default_repo_access):
    resp = client.get('/api/builds/{}/jobs'.format(default_build.id))
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert len(data) == 0
