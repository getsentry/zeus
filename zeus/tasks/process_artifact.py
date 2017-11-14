from flask import current_app

from zeus import auth
from zeus.artifacts import manager as default_manager
from zeus.config import celery, db
from zeus.constants import Result
from zeus.models import Artifact, Job, Status

from .aggregate_job_stats import aggregate_build_stats_for_job


@celery.task(max_retries=None)
def process_artifact(artifact_id, manager=None, **kwargs):
    artifact = Artifact.query.unrestricted_unsafe().select_for_update().get(artifact_id)
    if artifact is None:
        return

    artifact.status = Status.in_progress
    db.session.add(artifact)
    db.session.flush()

    auth.set_current_tenant(auth.Tenant(
        repository_ids=[artifact.repository_id]))

    job = Job.query.get(artifact.job_id)

    if job.result == Result.aborted:
        return

    if artifact.file:
        if manager is None:
            manager = default_manager

        with db.session.begin_nested():
            try:
                manager.process(artifact)
            except Exception:
                current_app.logger.exception(
                    'Unrecoverable exception processing artifact %s: %s', artifact.job_id, artifact
                )

    artifact.status = Status.finished
    db.session.add(artifact)
    db.session.commit()

    # we always aggregate results to avoid locking here
    aggregate_build_stats_for_job.delay(job_id=job.id)
