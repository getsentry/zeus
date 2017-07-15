from flask import current_app
from sqlalchemy.orm import joinedload

from zeus import auth
from zeus.artifacts import manager as default_manager
from zeus.config import celery
from zeus.constants import Result
from zeus.models import Artifact


@celery.task
def process_artifact(artifact_id, manager=None, **kwargs):
    artifact = Artifact.query.unrestricted_unsafe().options(
        joinedload('project'),
    ).get(artifact_id)
    if artifact is None:
        return

    auth.set_current_tenant(
        auth.Tenant(
            organization_ids=[artifact.organization_id],
            project_ids=[artifact.project_id],
            repository_ids=[artifact.project.repository_id],
        )
    )

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
