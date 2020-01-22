from datetime import timedelta
from flask import current_app

from zeus.config import celery, db
from zeus.constants import Status
from zeus.exceptions import UnknownJob
from zeus.models import Build, PendingArtifact
from zeus.utils import timezone

from .process_pending_artifact import process_pending_artifact


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
                "cleanup: process_pending_artifact %s [expired]", result.id
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
            "cleanup: process_pending_artifact %s [build_finished]", result.id
        )
        try:
            process_pending_artifact(pending_artifact_id=result.id)
        except UnknownJob:
            # do we just axe it?
            pass
