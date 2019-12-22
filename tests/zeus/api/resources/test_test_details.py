def test_test_details(
    client, default_login, default_testcase, default_repo, default_repo_access
):
    resp = client.get("/api/tests/{}".format(str(default_testcase.id)))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(default_testcase.id)
    assert data["hash"] == str(default_testcase.hash)
    assert data["name"] == default_testcase.name
