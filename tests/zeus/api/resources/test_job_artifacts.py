import json

from zeus.testutils import assert_json_response


def test_job_artifacts_list(client, default_login, default_job, default_artifact, default_repo_access):
    resp = client.get('/api/jobs/{}/artifacts'.format(default_job.id))
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]['id'] == str(default_artifact.id)


def test_job_artifacts_list_empty(client, default_login, default_job, default_repo_access):
    resp = client.get('/api/jobs/{}/artifacts'.format(default_job.id))
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert len(data) == 0
