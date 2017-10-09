from zeus.constants import Status
from zeus.tasks import process_artifact


def test_aggregates_upon_completion(mocker, default_artifact):
    manager = mocker.Mock()

    process_artifact(artifact_id=default_artifact.id, manager=manager)

    manager.process.assert_called_once_with(
        default_artifact,
    )

    assert default_artifact.status == Status.finished
