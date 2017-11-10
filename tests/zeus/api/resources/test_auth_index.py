def test_anonymous(client):
    resp = client.get('/api/auth')
    assert resp.status_code == 200
    data = resp.json()
    assert data == {'isAuthenticated': False}


def test_authenticated(client, default_login, default_user):
    resp = client.get('/api/auth')
    assert resp.status_code == 200
    data = resp.json()
    assert data['isAuthenticated'] is True
    assert data['user']['id'] == str(default_user.id)
    assert data['identities'] == []
    assert len(data['emails']) == 1
    assert data['emails'][0]['email'] == default_user.email


def test_authenticated_with_identity(client, default_login, default_user, default_identity):
    resp = client.get('/api/auth')
    assert resp.status_code == 200
    data = resp.json()
    assert data['isAuthenticated'] is True
    assert data['user']['id'] == str(default_user.id)
    assert len(data['identities']) == 1
    assert data['identities'][0]['id'] == str(default_identity.id)


def test_logout(client, default_login, default_user):
    resp = client.delete('/api/auth')
    assert resp.status_code == 200
    data = resp.json()
    assert data['isAuthenticated'] is False
    assert data == {'isAuthenticated': False, 'user': None}
