from flask import current_app

from zeus import auth
from zeus.artifacts import manager as default_manager
from zeus.config import celery, db
from zeus.constants import Result
from zeus.models import Artifact, Job, Status

from .aggregate_job_stats import aggregate_build_stats_for_job


@celery.task(max_retries=None, autoretry_for=(Exception,))
def process_artifact(artifact_id, manager=None, **kwargs):
    artifact = Artifact.query.unrestricted_unsafe().get(artifact_id)
    if artifact is None:
        current_app.logger.error('Artifact %s not found', artifact_id)
        return

    artifact.status = Status.in_progress
    db.session.add(artifact)
    db.session.flush()

    auth.set_current_tenant(auth.Tenant(
        repository_ids=[artifact.repository_id]))

    job = Job.query.get(artifact.job_id)

    if job.result == Result.aborted:
        current_app.logger.info(
            'Skipping artifact processing (%s) due to Job aborted', artifact_id)
        artifact.status = Status.finished
        db.session.add(artifact)
        db.session.commit()
        return

    if artifact.file:
        if manager is None:
            manager = default_manager

        try:
            with db.session.begin_nested():
                manager.process(artifact)
        except Exception:
            current_app.logger.exception(
                'Unrecoverable exception processing artifact %s: %s', artifact.job_id, artifact
            )
    else:
        current_app.logger.info(
            'Skipping artifact processing (%s) due to missing file', artifact_id)

    artifact.status = Status.finished
    db.session.add(artifact)
    db.session.commit()

    # we always aggregate results to avoid locking here
    aggregate_build_stats_for_job.delay(job_id=job.id)
