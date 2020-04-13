from datetime import timedelta

from zeus import factories
from zeus.constants import Result, Status
from zeus.models import Build, FailureReason
from zeus.tasks import cleanup_builds, cleanup_jobs
from zeus.utils import timezone


def test_cleanup_jobs_with_timed_out(
    mocker, db_session, default_build, default_revision
):
    job = factories.JobFactory.create(
        build=default_build,
        in_progress=True,
        date_updated=timezone.now() - timedelta(minutes=90),
    )

    cleanup_jobs()

    assert job.date_finished
    assert job.status == Status.finished
    assert job.result == Result.errored

    reasons = list(
        FailureReason.query.unrestricted_unsafe().filter(
            FailureReason.build_id == job.build_id
        )
    )
    assert len(reasons) == 1
    assert reasons[0].reason == FailureReason.Reason.timeout
    assert reasons[0].job_id == job.id
    assert reasons[0].build_id == job.build_id


def test_cleanup_jobs_with_no_date_updated(
    mocker, db_session, default_build, default_revision
):
    job = factories.JobFactory.create(
        build=default_build, in_progress=True, date_updated=None
    )

    cleanup_jobs()

    assert job.date_finished
    assert job.status == Status.finished
    assert job.result == Result.errored

    reasons = list(
        FailureReason.query.unrestricted_unsafe().filter(
            FailureReason.build_id == job.build_id
        )
    )
    assert len(reasons) == 1
    assert reasons[0].reason == FailureReason.Reason.internal_error
    assert reasons[0].job_id == job.id
    assert reasons[0].build_id == job.build_id


def test_cleanup_builds(mocker, db_session, default_build, default_revision):
    job = factories.JobFactory.create(
        build=default_build,
        in_progress=True,
        date_started=timezone.now() - timedelta(minutes=90),
    )
    # prevent resolve_ref
    default_build.revision_sha = default_revision.sha
    default_build.status = Status.in_progress
    default_build.date_started = job.date_started
    db_session.add(default_build)
    db_session.flush()

    cleanup_builds()

    assert job.date_finished
    assert job.status == Status.finished
    assert job.result == Result.errored

    build = Build.query.unrestricted_unsafe().get(job.build_id)

    assert build.date_finished == job.date_finished
    assert build.status == job.status
    assert build.result == job.result
