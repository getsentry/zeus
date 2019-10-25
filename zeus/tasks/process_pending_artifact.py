from flask import current_app
from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import celery, db
from zeus.constants import Status
from zeus.models import Artifact, Build, Job, PendingArtifact

from .process_artifact import process_artifact


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def process_pending_artifact(pending_artifact_id, **kwargs):
    pending_artifact = PendingArtifact.query.unrestricted_unsafe().get(
        pending_artifact_id
    )
    if pending_artifact is None:
        current_app.logger.error("PendingArtifact %s not found", pending_artifact_id)
        return

    db.session.delete(pending_artifact)
    db.session.flush()

    auth.set_current_tenant(
        auth.RepositoryTenant(repository_id=pending_artifact.repository_id)
    )

    build = Build.query.filter(
        Build.repository_id == pending_artifact.repository_id,
        Build.provider == pending_artifact.provider,
        Build.external_id == pending_artifact.external_build_id,
    ).first()
    if not build:
        raise NotImplementedError

    job = Job.query.filter(
        Job.repository_id == pending_artifact.repository_id,
        Job.build_id == build.id,
        Job.provider == pending_artifact.provider,
        Job.external_id == pending_artifact.external_job_id,
    ).first()
    if not job:
        raise NotImplementedError

    artifact = Artifact(
        job_id=job.id,
        repository_id=pending_artifact.repository_id,
        name=pending_artifact.name,
        status=Status.queued,
    )

    try:
        db.session.add(artifact)
        db.session.flush()
    except IntegrityError:
        current_app.logger.error(
            "Skipping pending artifact processing (%s) - duplicate key",
            pending_artifact_id,
        )
        # XXX(dcramer): this is more of an error but we make an assumption
        # that this happens because it was already sent
        db.session.rollback()
        db.session.delete(pending_artifact)
        db.session.commit()
        return

    artifact.file.save(
        pending_artifact.file,
        # XXX(dcramer): we reference the same file, so it lives in the old path
        # "{0}/{1}/{2}_{3}".format(
        #     job.id.hex[:4], job.id.hex[4:], artifact.id.hex, artifact.name
        # ),
    )
    db.session.add(artifact)

    if job.status == Status.finished:
        job.status = Status.collecting_results
        db.session.add(job)

    db.session.commit()

    process_artifact.delay(artifact_id=artifact.id)
