from datetime import timedelta
from flask import current_app
from sqlalchemy import or_

from zeus.config import celery, db
from zeus.constants import Result, Status
from zeus.exceptions import UnknownJob
from zeus.models import Artifact, Build, Job, PendingArtifact
from zeus.utils import timezone

from .aggregate_job_stats import aggregate_build_stats
from .process_artifact import process_artifact
from .process_pending_artifact import process_pending_artifact
from .resolve_ref import resolve_ref_for_build


@celery.task(name="zeus.cleanup_builds", time_limit=300)
def cleanup_builds(task_limit=100):
    cleanup_pending_artifacts(task_limit=task_limit)
    cleanup_artifacts(task_limit=task_limit)
    cleanup_jobs(task_limit=task_limit)
    cleanup_build_refs(task_limit=task_limit)
    cleanup_build_stats(task_limit=task_limit)


@celery.task(name="zeus.cleanup_pending_artifacts", time_limit=300)
def cleanup_pending_artifacts(task_limit=100):
    # find any pending artifacts which seemingly are stuck (not enqueued)
    queryset = (
        db.session.query(PendingArtifact.id)
        .filter(
            Build.external_id == PendingArtifact.external_build_id,
            Build.provider == PendingArtifact.provider,
            Build.repository_id == PendingArtifact.repository_id,
            Build.status == Status.finished,
        )
        .limit(task_limit)
    )

    for result in queryset:
        current_app.logger.warning("cleanup: process_pending_artifact  %s", result.id)
        try:
            process_pending_artifact(pending_artifact_id=result.id)
        except UnknownJob:
            # do we just axe it?
            pass


@celery.task(name="zeus.cleanup_artifacts", time_limit=300)
def cleanup_artifacts(task_limit=100):
    # find any artifacts which seemingly are stuck (not enqueued)
    queryset = (
        Artifact.query.unrestricted_unsafe()
        .filter(
            Artifact.status != Status.finished,
            or_(
                Artifact.date_updated < timezone.now() - timedelta(minutes=15),
                Artifact.date_updated == None,  # NOQA
            ),
        )
        .limit(task_limit)
    )
    for result in queryset:
        Artifact.query.unrestricted_unsafe().filter(
            Artifact.status != Status.finished, Artifact.id == result.id
        ).update({"date_updated": timezone.now()})
        db.session.flush()
        current_app.logger.warning("cleanup: process_artifact %s", result.id)
        process_artifact(artifact_id=result.id)


@celery.task(name="zeus.cleanup_jobs", time_limit=300)
def cleanup_jobs(task_limit=100):
    # timeout any jobs which have been sitting for far too long
    Job.query.unrestricted_unsafe().filter(
        Job.status != Status.finished,
        or_(
            Job.date_updated < timezone.now() - timedelta(hours=1),
            Job.date_updated == None,  # NOQA
        ),
    ).update(
        {
            "status": Status.finished,
            "result": Result.errored,
            "date_updated": timezone.now(),
            "date_finished": timezone.now(),
        }
    )
    db.session.commit()


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
            current_app.logger.exception("cleanup: resolve_ref_for_build %s", build.id)
