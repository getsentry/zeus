from datetime import timedelta
from flask import current_app

from zeus.config import celery, db
from zeus.models import PendingArtifact
from zeus.utils import timezone


@celery.task(name="zeus.cleanup_pending_artifacts", time_limit=300)
def cleanup_pending_artifacts():
    queryset = (
        PendingArtifact.query.unrestricted_unsafe()
        .filter(PendingArtifact.date_created < timezone.now() - timedelta(days=1))
        .limit(1000)
    )
    for result in queryset:
        current_app.logger.warning("deleting expired PendingArtifact %s", result.id)
        if result.file:
            result.file.delete()
        db.session.delete(result)
        db.session.commit()
