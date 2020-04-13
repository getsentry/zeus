from zeus import factories
from zeus.constants import Result, Status
from zeus.models import Job


def test_build_jobs_list(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    resp = client.get(
        "/api/repos/{}/builds/{}/jobs".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(default_job.id)


def test_build_jobs_list_empty(
    client, default_login, default_repo, default_build, default_repo_access
):
    resp = client.get(
        "/api/repos/{}/builds/{}/jobs".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_build_job_create(
    client, default_login, default_repo, default_build, default_repo_access
):
    resp = client.post(
        "/api/repos/{}/builds/{}/jobs".format(
            default_repo.get_full_name(), default_build.number
        ),
        json={"status": "queued"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"]

    job = Job.query.unrestricted_unsafe().get(data["id"])
    assert job.status == Status.queued
    assert job.result == Result.unknown
    assert job.build_id == default_build.id
    assert job.repository_id == default_repo.id
    assert job.date_updated
    assert not job.date_started
    assert not job.date_finished


def test_build_job_create_existing_entity(
    client, default_login, default_repo, default_build, default_repo_access
):
    existing_job = factories.JobFactory(build=default_build, travis=True)

    resp = client.post(
        "/api/repos/{}/builds/{}/jobs".format(
            default_repo.get_full_name(), default_build.number
        ),
        json={
            "provider": existing_job.provider,
            "external_id": existing_job.external_id,
        },
    )
    assert resp.status_code == 422
