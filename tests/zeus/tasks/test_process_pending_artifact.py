from zeus import factories
from zeus.models import Artifact, PendingArtifact
from zeus.tasks import process_pending_artifact


def test_aggregates_upon_completion(mocker, default_hook):
    build = factories.BuildFactory(travis=True, repository=default_hook.repository)

    job = factories.JobFactory(travis=True, build=build)

    pending_artifact = factories.PendingArtifactFactory(
        external_build_id=build.external_id,
        external_job_id=job.external_id,
        hook=default_hook,
    )

    pa_name = pending_artifact.name
    pa_size = pending_artifact.file.size
    pa_path = pending_artifact.file.path
    pa_filename = pending_artifact.file.filename

    process_pending_artifact(pending_artifact_id=pending_artifact.id)

    artifact = (
        Artifact.query.unrestricted_unsafe().filter(Artifact.job_id == job.id).first()
    )
    assert artifact.name == pa_name
    assert artifact.file.path == pa_path
    assert artifact.file.size == pa_size
    assert artifact.file.filename == pa_filename

    assert not PendingArtifact.query.get(pending_artifact.id)
