from datetime import datetime

from zeus import factories
from zeus.constants import Result, Status
from zeus.utils import timezone


def test_job_details(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    resp = client.get(
        "/api/repos/{}/builds/{}/jobs/{}".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(default_job.id)


def test_update_job_to_finished(
    client, mocker, default_login, default_repo, default_build, default_repo_access
):
    job = factories.JobFactory(build=default_build, in_progress=True)

    mock_delay = mocker.patch("zeus.tasks.aggregate_build_stats_for_job.delay")

    resp = client.put(
        "/api/repos/{}/builds/{}/jobs/{}".format(
            default_repo.get_full_name(), default_build.number, job.number
        ),
        json={
            "result": "failed",
            "status": "finished",
            "started_at": "2017-01-01T01:02:30Z",
            "finished_at": "2017-01-01T01:22:30Z",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(job.id)

    assert job.status == Status.finished
    assert job.result == Result.failed
    assert job.date_started == datetime(2017, 1, 1, 1, 2, 30, tzinfo=timezone.utc)
    assert job.date_finished == datetime(2017, 1, 1, 1, 22, 30, tzinfo=timezone.utc)

    mock_delay.assert_called_once_with(job_id=job.id)


def test_update_job_to_in_progress(
    client, mocker, default_login, default_repo, default_build, default_repo_access
):
    job = factories.JobFactory(build=default_build, queued=True)

    mock_delay = mocker.patch("zeus.tasks.aggregate_build_stats_for_job.delay")

    resp = client.put(
        "/api/repos/{}/builds/{}/jobs/{}".format(
            default_repo.get_full_name(), default_build.number, job.number
        ),
        json={"status": "in_progress"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(job.id)

    assert job.status == Status.in_progress
    assert job.date_started
    assert not job.date_finished

    mock_delay.assert_called_once_with(job_id=job.id)


def test_update_job_to_finished_with_pending_artifacts(
    client,
    mocker,
    default_login,
    default_repo,
    default_build,
    default_job,
    default_repo_access,
):
    factories.ArtifactFactory(job=default_job, queued=True)

    assert default_job.result != Result.failed

    mock_delay = mocker.patch("zeus.tasks.aggregate_build_stats_for_job.delay")

    resp = client.put(
        "/api/repos/{}/builds/{}/jobs/{}".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        ),
        json={"result": "failed", "status": "finished"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(default_job.id)

    assert default_job.status == Status.collecting_results
    assert default_job.result == Result.failed

    mock_delay.assert_called_once_with(job_id=default_job.id)


def test_update_job_restart(
    client, mocker, default_login, default_repo, default_build, default_repo_access
):
    job = factories.JobFactory(build=default_build, finished=True, passed=True)

    mock_delay = mocker.patch("zeus.tasks.aggregate_build_stats_for_job.delay")

    resp = client.put(
        "/api/repos/{}/builds/{}/jobs/{}".format(
            default_repo.get_full_name(), default_build.number, job.number
        ),
        json={"status": "in_progress"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(job.id)

    assert job.status == Status.in_progress
    assert job.result == Result.unknown
    assert job.date_started
    assert not job.date_finished

    mock_delay.assert_called_once_with(job_id=job.id)
