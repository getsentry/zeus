import json

from zeus.testutils import assert_json_response


def test_build_details(client, default_login, default_build, default_repo_access):
    resp = client.get('/api/builds/{}'.format(default_build.id))
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert data['id'] == str(default_build.id)
