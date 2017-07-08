def test_anonymous(client):
    resp = client.get('/api/auth')
    assert resp.status_code == 200
    data = resp.json()
    assert data == {'isAuthenticated': False, 'user': None}


def test_authenticated(client, default_login, default_user):
    resp = client.get('/api/auth')
    assert resp.status_code == 200
    data = resp.json()
    assert data['isAuthenticated'] is True
    assert data['user']['id'] == str(default_user.id)


def test_logout(client, default_login, default_user):
    resp = client.delete('/api/auth')
    assert resp.status_code == 200
    data = resp.json()
    assert data['isAuthenticated'] is False
    assert data == {'isAuthenticated': False, 'user': None}
