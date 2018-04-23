from zeus.constants import Result
from zeus.models import TestCase as ZeusTestCase


def test_new_test(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    resp = client.post(
        "/api/repos/{}/builds/{}/jobs/{}/tests".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        ),
        json={"name": "example.test.case", "result": "failed"},
    )
    assert resp.status_code == 201
    data = resp.json()
    testcase = ZeusTestCase.query.unrestricted_unsafe().get(data["id"])
    assert testcase
    assert testcase.result == Result.failed
    assert testcase.name == "example.test.case"


def test_upsert_existing_test(
    client,
    default_login,
    default_repo,
    default_build,
    default_job,
    default_repo_access,
    default_testcase,
):
    resp = client.post(
        "/api/repos/{}/builds/{}/jobs/{}/tests".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        ),
        json={"name": default_testcase.name, "result": "failed"},
    )
    assert resp.status_code == 202
    data = resp.json()
    testcase = ZeusTestCase.query.unrestricted_unsafe().get(data["id"])
    assert testcase
    assert testcase.result == Result.failed
    assert testcase.name == default_testcase.name


def test_upsert_existing_test_no_changes(
    client,
    default_login,
    default_repo,
    default_build,
    default_job,
    default_repo_access,
    default_testcase,
):
    resp = client.post(
        "/api/repos/{}/builds/{}/jobs/{}/tests".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        ),
        json={"name": default_testcase.name, "result": "passed"},
    )
    assert resp.status_code == 200
    data = resp.json()
    testcase = ZeusTestCase.query.unrestricted_unsafe().get(data["id"])
    assert testcase
    assert testcase.result == Result.passed
    assert testcase.name == default_testcase.name
