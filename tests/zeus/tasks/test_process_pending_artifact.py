from zeus import factories
from zeus.models import Artifact
from zeus.tasks import process_pending_artifact


def test_aggregates_upon_completion(mocker, default_hook):
    build = factories.BuildFactory(travis=True, repository=default_hook.repository)

    job = factories.JobFactory(travis=True, build=build)

    pending_artifact = factories.PendingArtifactFactory(
        external_build_id=build.external_id,
        external_job_id=job.external_id,
        hook=default_hook,
    )

    process_pending_artifact(pending_artifact_id=pending_artifact.id)

    artifact = (
        Artifact.query.unrestricted_unsafe().filter(Artifact.job_id == job.id).first()
    )
    assert artifact.name == pending_artifact.name
    assert artifact.file.path == pending_artifact.file.path
    assert artifact.file.size == pending_artifact.file.size
    assert artifact.file.filename == pending_artifact.file.filename
