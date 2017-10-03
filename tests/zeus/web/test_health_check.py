import json


def test_simple(client):
    resp = client.get('/_health')
    assert resp.status_code == 200
    assert json.loads(resp.data) == {
        'ok': True,
    }
