from zeus.tasks.process_artifact import process_artifact


def test_simple(mocker, default_artifact):
    manager = mocker.Mock()

    process_artifact(artifact_id=default_artifact.id, manager=manager)

    manager.process.assert_called_once_with(
        default_artifact,
    )
