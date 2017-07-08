import json

from zeus.testutils import assert_json_response


def test_job_details(client, default_login, default_job, default_repo_access):
    resp = client.get('/api/jobs/{}'.format(default_job.id))
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert data['id'] == str(default_job.id)
