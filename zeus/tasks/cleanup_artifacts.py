from datetime import timedelta
from flask import current_app
from sqlalchemy import or_

from zeus.config import celery, db
from zeus.constants import Status
from zeus.models import Artifact
from zeus.utils import timezone

from .process_artifact import process_artifact


@celery.task(name="zeus.cleanup_artifacts", time_limit=300)
def cleanup_artifacts(task_limit=100):
    # remove expired artifacts
    queryset = (
        Artifact.query.unrestricted_unsafe()
        .filter(
            Artifact.status != Status.expired,
            Artifact.date_created
            < timezone.now() - current_app.config["ARTIFACT_RETENTION"],
        )
        .limit(task_limit)
    )
    for result in queryset:
        current_app.logger.warning("cleanup: process_artifact %s [expired]", result.id)
        Artifact.query.unrestricted_unsafe().filter(
            Artifact.status != Status.expired, Artifact.id == result.id
        ).update({"status": Status.expired})
        if result.file:
            result.file.delete()
        db.session.commit()

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
        current_app.logger.warning(
            "cleanup: process_artifact %s [processed]", result.id
        )
        process_artifact(artifact_id=result.id)
