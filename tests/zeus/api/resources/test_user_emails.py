def test_user_email_list(client, default_login):
    resp = client.get("/api/users/me/emails")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["email"] == default_login.email
