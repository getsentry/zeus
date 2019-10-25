from zeus.config import db
from zeus.constants import Status
from zeus.models import Artifact, Job, PendingArtifact


def has_unprocessed_artifacts(job: Job) -> bool:
    if db.session.query(
        Artifact.query.filter(
            Artifact.status != Status.finished, Artifact.job_id == job.id
        ).exists()
    ).scalar():
        return True
    if (
        job.external_id
        and db.session.query(
            PendingArtifact.query.filter(
                PendingArtifact.repository_id == job.repository_id,
                PendingArtifact.provider == job.provider,
                PendingArtifact.external_build_id == job.build.external_id,
                PendingArtifact.external_job_id == job.external_id,
            ).exists()
        ).scalar()
    ):
        return True
    return False
