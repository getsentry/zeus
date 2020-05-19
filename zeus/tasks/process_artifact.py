import sentry_sdk

from datetime import timedelta
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
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("artifact_id", str(artifact_id))

    artifact = Artifact.query.unrestricted_unsafe().get(artifact_id)
    if artifact is None:
        current_app.logger.error(
            "process-artifact.not-found",
            extra={"artifact_id": artifact_id, "job_id": artifact.job_id},
        )
        return

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("job_id", str(artifact.job_id))
        scope.set_tag("repository_id", str(artifact.repository_id))

    if artifact.status == Status.finished and not force:
        current_app.logger.info(
            "process-artifact.already-finished",
            extra={"artifact_id": artifact_id, "job_id": artifact.job_id},
        )
        return

    if (
        artifact.status == Status.in_progress
        and not force
        and artifact.date_started > timezone.now() - timedelta(minutes=15)
    ):
        current_app.logger.warning(
            "process-artifact.already-in-progress",
            extra={"artifact_id": artifact_id, "job_id": artifact.job_id},
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
            "process-artifact.job-aborted",
            extra={"artifact_id": artifact_id, "job_id": artifact.job_id},
        )
        artifact.status = Status.finished
        db.session.add(artifact)
        db.session.commit()
        return

    build = Build.query.get(job.build_id)
    if build.result == Result.errored:
        current_app.logger.info(
            "process-artifact.build-errored",
            extra={"artifact_id": artifact_id, "job_id": artifact.job_id},
        )
        artifact.status = Status.finished
        db.session.add(artifact)
        db.session.commit()
        return

    if not build.revision_sha:
        if manager:
            raise Exception("Cannot process artifact until revision is resolved")
        current_app.logger.info(
            "process-artifact.unresolved-revision",
            extra={"artifact_id": artifact_id, "job_id": artifact.job_id},
        )
        return celery.apply_async(
            "zeus.process_artifact",
            kwargs={"artifact_id": artifact_id, "force": force},
            countdown=15,
            **kwargs
        )

    if artifact.file:
        if manager is None:
            manager = default_manager

        try:
            with db.session.begin_nested():
                manager.process(artifact)
        except Exception:
            current_app.logger.exception(
                "process-artifact.unrecoverable-error",
                extra={"artifact_id": artifact_id, "job_id": artifact.job_id},
            )

    else:
        current_app.logger.warning(
            "process-artifact.missing-file",
            extra={"artifact_id": artifact_id, "job_id": artifact.job_id},
        )

    artifact.status = Status.finished
    artifact.date_finished = timezone.now()
    db.session.add(artifact)
    db.session.commit()

    # we always aggregate results to avoid locking here
    celery.delay("zeus.aggregate_build_stats_for_job", job_id=job.id)
