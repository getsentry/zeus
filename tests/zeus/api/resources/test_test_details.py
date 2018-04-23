from zeus.constants import Result


def test_test_details(client, default_login, default_testcase, default_repo_access):
    resp = client.get("/api/tests/{}".format(default_testcase.id))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(default_testcase.id)
    assert data["message"] == default_testcase.message


def test_test_update(client, default_login, default_testcase, default_repo_access):
    resp = client.put(
        "/api/tests/{}".format(default_testcase.id),
        json={"result": "failed", "message": "we failed hard"},
    )
    assert resp.status_code == 200
    assert default_testcase.result == Result.failed
    assert default_testcase.message == "we failed hard"
