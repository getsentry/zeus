def test_installation_details(client, default_user, default_build):
    resp = client.get("/api/install")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stats"] == {
        "builds24h": 1,
        "buildsTotal": 1,
        "reposTotal": 1,
        "usersTotal": 1,
    }
    assert data["config"]["debug"] is False
    assert data["config"]["environment"]
    assert data["config"]["release"]
    assert data["config"]["streamUrl"] == "http://localhost:8090/stream"
