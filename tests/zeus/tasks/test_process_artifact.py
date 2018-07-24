from zeus import factories
from zeus.constants import Status
from zeus.tasks import process_artifact


def test_aggregates_upon_completion(mocker, default_job):
    manager = mocker.Mock()

    artifact = factories.ArtifactFactory(job=default_job, queued=True)

    process_artifact(artifact_id=artifact.id, manager=manager)

    assert artifact.status == Status.finished

    manager.process.assert_called_once_with(artifact)
