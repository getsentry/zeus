import json

from zeus.testutils import assert_json_response


def test_anonymous(client):
    resp = client.get('/api/auth/')
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert data == {'isAuthenticated': False, 'user': None}


def test_authenticated(client, default_login, default_user):
    resp = client.get('/api/auth/')
    assert resp.status_code == 200
    assert_json_response(resp)
    data = json.loads(resp.data)
    assert data['isAuthenticated'] is True
    assert data['user']['id'] == str(default_user.id)
