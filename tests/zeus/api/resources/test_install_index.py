def test_installation_details(client, default_user, default_build):
    resp = client.get("/api/install")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stats"]["builds"] == {
        "created": {"24h": 1, "30d": 1},
        "errored": {"24h": 0, "30d": 0},
    }
    assert data["stats"]["jobs"] == {
        "created": {"24h": 0, "30d": 0},
        "errored": {"24h": 0, "30d": 0},
    }
    assert data["stats"]["repos"] == {"active": {"24h": 1, "30d": 1}}
    assert data["stats"]["users"] == {"active": {"24h": 1, "30d": 1}}
    assert data["config"]["debug"] is False
    assert data["config"]["environment"]
    assert data["config"]["release"]
    assert data["config"]["pubsubEndpoint"] == "http://localhost:8090"
