from flask import current_app

from zeus.config import db, queue
from zeus.constants import Status
from zeus.models import Artifact
from zeus.utils import timezone


@queue.task(name="zeus.cleanup_artifacts")
def cleanup_artifacts():
    queryset = (
        Artifact.query.unrestricted_unsafe()
        .filter(
            Artifact.status != Status.expired,
            Artifact.date_created
            < timezone.now() - current_app.config["ARTIFACT_RETENTION"],
        )
        .limit(1000)
    )
    for result in queryset:
        Artifact.query.unrestricted_unsafe().filter(
            Artifact.status != Status.expired, Artifact.id == result.id
        ).update({"status": Status.expired})
        if result.file:
            result.file.delete()
        db.session.commit()
