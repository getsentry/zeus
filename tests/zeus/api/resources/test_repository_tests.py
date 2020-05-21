from datetime import timedelta
from zeus import factories


def test_repository_tests(
    client, default_login, default_build, default_job, default_repo, default_repo_access
):
    factories.TestCaseRollupFactory(
        repository=default_repo,
        name="a.test",
        date=default_job.date_finished.date(),
        hash="a" * 32,
        runs_failed=3,
        runs_passed=5,
        total_duration=80,
    )
    factories.TestCaseRollupFactory(
        repository=default_repo,
        name="a.test",
        hash="a" * 32,
        date=default_job.date_finished.date() - timedelta(days=1),
        runs_failed=0,
        runs_passed=2,
        total_duration=40,
    )
    factories.TestCaseRollupFactory(
        repository=default_repo,
        name="another.test",
        hash="b" * 32,
        date=default_job.date_finished.date(),
        runs_failed=8,
        runs_passed=0,
        total_duration=240,
    )

    resp = client.get("/api/repos/{}/tests".format(default_repo.get_full_name()))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0] == {
        "name": "another.test",
        "hash": "b" * 32,
        "runs_failed": 8,
        "total_runs": 8,
        "avg_duration": 30,
    }
    assert data[1] == {
        "name": "a.test",
        "hash": "a" * 32,
        "runs_failed": 3,
        "total_runs": 10,
        "avg_duration": 12,
    }
