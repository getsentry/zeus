from datetime import timedelta
from flask import current_app

from zeus.config import celery, db
from zeus.constants import Status
from zeus.exceptions import UnknownJob
from zeus.models import Build, PendingArtifact
from zeus.utils import timezone


@celery.task(name="zeus.cleanup_pending_artifacts", time_limit=300)
def cleanup_pending_artifacts(task_limit=100):

    queryset = (
        PendingArtifact.query.unrestricted_unsafe()
        .filter(PendingArtifact.date_created < timezone.now() - timedelta(days=1))
        .limit(1000)
    )
    for result in queryset:
        with db.session.begin_nested():
            current_app.logger.warning(
                "cleanup-pending-artifacts.expired",
                extra={
                    "pending_artifact_id": result.id,
                    "external_build_id": result.external_build_id,
                    "external_job_id": result.external_job_id,
                },
            )
            if result.file:
                result.file.delete()
            db.session.delete(result)
        db.session.commit()

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
        current_app.logger.warning(
            "cleanup-pending-artifacts.finished-build",
            extra={
                "pending_artifact_id": result.id,
                "external_build_id": result.external_build_id,
                "external_job_id": result.external_job_id,
            },
        )
        try:
            celery.delay("zeus.process_pending_artifact", pending_artifact_id=result.id)
        except UnknownJob:
            current_app.logger.warning(
                "cleanup-pending-artifacts.unknown-job",
                extra={
                    "pending_artifact_id": result.id,
                    "external_build_id": result.external_build_id,
                    "external_job_id": result.external_job_id,
                },
            )
            # do we just axe it?
            pass
