import json


def test_simple(client):
    resp = client.get('/healthz')
    assert resp.status_code == 200
    assert json.loads(resp.data) == {
        'ok': True,
    }
