from flask import current_app

from zeus import auth
from zeus.artifacts import manager as default_manager
from zeus.config import celery
from zeus.constants import Result
from zeus.models import Artifact


@celery.task
def process_artifact(artifact_id, manager=None, **kwargs):
    artifact = Artifact.query.unrestricted_unsafe().get(artifact_id)
    if artifact is None:
        return

    auth.set_current_tenant(auth.Tenant(repository_ids=[artifact.repository_id]))

    if not artifact.file:
        return

    job = artifact.job

    if job.result == Result.aborted:
        return

    if manager is None:
        manager = default_manager

    try:
        manager.process(artifact)
    except Exception:
        current_app.logger.exception(
            'Unrecoverable exception processing artifact %s: %s', artifact.job_id, artifact
        )
