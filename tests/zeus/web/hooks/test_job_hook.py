from zeus import factories
from zeus.constants import Result, Status
from zeus.models import Job


def test_new_job(client, default_source, default_repo, default_hook):
    build = factories.BuildFactory(
        source=default_source, provider=default_hook.provider, external_id="3"
    )

    job_xid = "2"

    path = "/hooks/{}/{}/builds/{}/jobs/{}".format(
        default_hook.id, default_hook.get_signature(), build.external_id, job_xid
    )

    payload = {"result": "passed", "status": "finished"}

    resp = client.post(path, json=payload)
    assert resp.status_code == 200, repr(resp.data)

    job = Job.query.unrestricted_unsafe().get(resp.json()["id"])
    assert job
    assert job.build_id == build.id
    assert job.repository_id == build.repository_id
    assert job.provider == default_hook.provider
    assert job.external_id == job_xid
    assert job.result == Result.passed
    assert job.status == Status.finished


def test_existing_job(client, default_source, default_repo, default_hook):
    build = factories.BuildFactory(
        source=default_source, provider=default_hook.provider, external_id="3"
    )

    job = factories.JobFactory(
        build=build, provider=default_hook.provider, external_id="2", in_progress=True
    )

    path = "/hooks/{}/{}/builds/{}/jobs/{}".format(
        default_hook.id,
        default_hook.get_signature(),
        build.external_id,
        job.external_id,
    )

    payload = {"result": "passed", "status": "finished"}

    resp = client.post(path, json=payload)
    assert resp.status_code == 200, repr(resp.data)
    data = resp.json()
    assert data["result"] == "passed"
    assert data["status"] == "finished"

    job = Job.query.unrestricted_unsafe().get(job.id)

    assert job.result == Result.passed
    assert job.status == Status.finished
