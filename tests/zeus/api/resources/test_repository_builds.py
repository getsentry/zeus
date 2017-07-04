import json

from zeus.testutils import assert_json_response


def test_repo_build_list(client, default_login, default_build, default_repo, default_repo_access):
    resp = client.get('/api/repos/{}/builds'.format(default_repo.id.hex))
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]['id'] == str(default_build.id)


def test_repo_build_list_without_access(client, default_login, default_build, default_repo):
    resp = client.get('/api/repos/{}/builds'.format(default_repo.id.hex))
    assert resp.status_code == 404
