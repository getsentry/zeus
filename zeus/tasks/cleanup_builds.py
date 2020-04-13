from datetime import timedelta
from flask import current_app
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError

from zeus.config import celery, db
from zeus.constants import Result, Status
from zeus.models import Build, FailureReason, Job
from zeus.utils import timezone

from .aggregate_job_stats import aggregate_build_stats
from .resolve_ref import resolve_ref_for_build


@celery.task(name="zeus.cleanup_builds", time_limit=300)
def cleanup_builds(task_limit=100):
    current_app.logger.info("cleanup: running cleanup_jobs")
    cleanup_jobs(task_limit=task_limit)
    current_app.logger.info("cleanup: running cleanup_build_refs")
    cleanup_build_refs(task_limit=task_limit)
    current_app.logger.info("cleanup: running cleanup_build_stats")
    cleanup_build_stats(task_limit=task_limit)


@celery.task(name="zeus.cleanup_jobs", time_limit=300)
def cleanup_jobs(task_limit=100):
    # timeout any jobs which have been sitting for far too long
    qs = Job.query.unrestricted_unsafe().filter(
        Job.status != Status.finished,
        or_(
            Job.date_updated < timezone.now() - timedelta(hours=1),
            and_(Job.date_updated == None, Job.status != Status.queued),  # NOQA
        ),
    )
    results = 0
    for job in qs:
        results += 1

        if job.date_updated:
            reason = FailureReason.Reason.timeout
        else:
            current_app.logger.error(
                "cleanup: Job (id=%s) with no date_updated", job.id
            )
            reason = FailureReason.Reason.internal_error

        job.status = Status.finished
        job.result = Result.errored
        job.date_updated = timezone.now()
        job.date_finished = job.date_updated
        db.session.add(job)
        try:
            with db.session.begin_nested():
                db.session.add(
                    FailureReason(
                        repository_id=job.repository_id,
                        build_id=job.build_id,
                        job_id=job.id,
                        reason=reason,
                    )
                )
                db.session.flush()
        except IntegrityError as exc:
            if "duplicate" not in str(exc):
                raise
        db.session.commit()

    if results:
        current_app.logger.warning("cleanup: cleanup_jobs affected rows %s", results)


@celery.task(name="zeus.cleanup_build_refs", time_limit=300)
def cleanup_build_refs(task_limit=100):
    # attempt to resolve refs which never applied
    queryset = (
        Build.query.unrestricted_unsafe()
        .filter(
            Build.ref != None,  # NOQA
            Build.revision_sha == None,  # NOQA
            Build.result != Result.errored,
            Build.date_created < timezone.now() - timedelta(minutes=15),
        )
        .limit(task_limit)
    )
    for build in queryset:
        current_app.logger.warning("cleanup: resolve_ref_for_build %s", build.id)
        try:
            resolve_ref_for_build(build_id=build.id)
        except Exception:
            current_app.logger.exception("cleanup: resolve_ref_for_build %s", build.id)


@celery.task(name="zeus.cleanup_build_stats", time_limit=300)
def cleanup_build_stats(task_limit=100):
    # find any builds which should be marked as finished but aren't
    queryset = (
        Build.query.unrestricted_unsafe()
        .filter(
            Build.status != Status.finished,
            Build.date_started < timezone.now() - timedelta(minutes=15),
            ~Job.query.filter(
                Job.build_id == Build.id, Job.status != Status.finished
            ).exists(),
        )
        .limit(task_limit)
    )
    for build in queryset:
        current_app.logger.warning("cleanup: aggregate_build_stats %s", build.id)
        try:
            aggregate_build_stats(build_id=build.id)
        except Exception:
            current_app.logger.exception("cleanup: aggregate_build_stats %s", build.id)

    results = (
        Build.query.unrestricted_unsafe()
        .filter(Build.status != Status.finished, Build.result == Result.errored)
        .update({"status": Status.finished})
    )
    if results:
        current_app.logger.warning(
            "cleanup: cleanup_build_stats [unfinished; errored] affected rows %s",
            results,
        )
    db.session.commit()
