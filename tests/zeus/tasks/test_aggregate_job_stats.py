from zeus import auth, factories
from zeus.constants import Result, Status
from zeus.tasks import aggregate_build_stats_for_job


def test_unfinished_job(mocker, db_session, default_source):
    auth.set_current_tenant(auth.Tenant(repository_ids=[default_source.repository_id]))

    build = factories.BuildFactory(source=default_source, queued=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, in_progress=True)
    db_session.add(job)

    aggregate_build_stats_for_job(job.id)

    assert build.status == Status.in_progress
    assert build.result == Result.unknown


def test_finished_job(mocker, db_session, default_source):
    auth.set_current_tenant(auth.Tenant(repository_ids=[default_source.repository_id]))

    build = factories.BuildFactory(source=default_source, in_progress=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, failed=True)
    db_session.add(job)

    aggregate_build_stats_for_job(job.id)

    assert build.status == Status.finished
    assert build.result == Result.failed
