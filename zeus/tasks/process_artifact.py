from flask import current_app

from zeus import auth
from zeus.artifacts import manager as default_manager
from zeus.config import celery, db
from zeus.constants import Result
from zeus.models import Artifact, Build, Job, Status
from zeus.utils import timezone


@celery.task(
    name="zeus.process_artifact",
    max_retries=5,
    autoretry_for=(Exception,),
    acks_late=True,
    time_limit=60,
)
def process_artifact(artifact_id, manager=None, force=False, countdown=None, **kwargs):
    artifact = Artifact.query.unrestricted_unsafe().get(artifact_id)
    if artifact is None:
        current_app.logger.error("Artifact %s not found", artifact_id)
        return

    if artifact.status == Status.finished and not force:
        current_app.logger.info(
            "Skipping artifact processing (%s) - already marked as finished",
            artifact_id,
        )
        return

    artifact.status = Status.in_progress
    artifact.date_started = timezone.now()
    db.session.add(artifact)
    db.session.flush()

    auth.set_current_tenant(auth.RepositoryTenant(repository_id=artifact.repository_id))

    job = Job.query.get(artifact.job_id)

    if job.result == Result.aborted:
        current_app.logger.info(
            "Skipping artifact processing (%s) - Job aborted", artifact_id
        )
        artifact.status = Status.finished
        db.session.add(artifact)
        db.session.commit()
        return

    build = Build.query.get(job.build_id)
    if build.result == Result.errored:
        current_app.logger.info(
            "Skipping artifact processing (%s) - Build errored", artifact_id
        )
        artifact.status = Status.finished
        db.session.add(artifact)
        db.session.commit()
        return

    if not build.revision_sha:
        if manager:
            raise Exception("Cannot process artifact until revision is resolved")
        return celery.delay(
            "zeus.process_artifact", artifact_id, force=force, countdown=5, **kwargs
        )

    if artifact.file:
        if manager is None:
            manager = default_manager

        try:
            with db.session.begin_nested():
                manager.process(artifact)
        except Exception:
            current_app.logger.exception(
                "Unrecoverable exception processing artifact %s: %s",
                artifact.job_id,
                artifact,
            )
    else:
        current_app.logger.info(
            "Skipping artifact processing (%s) due to missing file", artifact_id
        )

    artifact.status = Status.finished
    artifact.date_finished = timezone.now()
    db.session.add(artifact)
    db.session.commit()

    # we always aggregate results to avoid locking here
    celery.delay("zeus.aggregate_build_stats_for_job", job_id=job.id)
