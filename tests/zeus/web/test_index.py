def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
