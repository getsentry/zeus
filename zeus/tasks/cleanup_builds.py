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
def cleanup_builds():
    # find any pending artifacts which seemingly are stuck (not enqueued)
    queryset = (
        db.session.query(PendingArtifact.id)
        .filter(
            Build.external_id == PendingArtifact.external_build_id,
            Build.provider == PendingArtifact.provider,
            Build.repository_id == PendingArtifact.repository_id,
            Build.status == Status.finished,
        )
        .limit(100)
    )

    for result in queryset:
        current_app.logger.warning("cleanup: process_pending_artifact  %s", result.id)
        try:
            process_pending_artifact(pending_artifact_id=result.id)
        except UnknownJob:
            # do we just axe it?
            pass

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
        .limit(100)
    )
    for result in queryset:
        Artifact.query.unrestricted_unsafe().filter(
            Artifact.status != Status.finished, Artifact.id == result.id
        ).update({"date_updated": timezone.now()})
        db.session.flush()
        current_app.logger.warning("cleanup: process_artifact %s", result.id)
        process_artifact(artifact_id=result.id)

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

    # attempt to resolve refs which never applied
    queryset = (
        Build.query.unrestricted_unsafe()
        .filter(
            Build.ref != None,  # NOQA
            Build.revision_sha == None,  # NOQA
            Build.date_created < timezone.now() - timedelta(minutes=15),
        )
        .limit(100)
    )
    for build in queryset:
        current_app.logger.warning("cleanup: resolve_ref_for_build %s", build.id)
        resolve_ref_for_build(build_id=build.id)

    # find any builds which should be marked as finished but aren't
    queryset = (
        Build.query.unrestricted_unsafe()
        .filter(
            Build.status != Status.finished,
            ~Job.query.filter(
                Job.build_id == Build.id, Job.status != Status.finished
            ).exists(),
        )
        .limit(100)
    )
    for build in queryset:
        current_app.logger.warning("cleanup: aggregate_build_stats %s", build.id)
        aggregate_build_stats(build_id=build.id)
