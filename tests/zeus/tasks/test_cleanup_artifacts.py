from datetime import timedelta

from zeus import factories
from zeus.constants import Status
from zeus.tasks import cleanup_artifacts
from zeus.utils import timezone


def test_cleanup_artifacts_already_finished(mocker, db_session):
    mock_process_artifact = mocker.Mock()

    artifact = factories.ArtifactFactory.create(
        job=factories.JobFactory(finished=True), status=Status.finished
    )

    cleanup_artifacts(_process_artifact=mock_process_artifact)

    assert not mock_process_artifact.mock_calls
    assert artifact.status == Status.finished


def test_cleanup_artifacts_stuck(mocker, db_session):
    mock_process_artifact = mocker.Mock()

    artifact = factories.ArtifactFactory.create(
        job=factories.JobFactory(finished=True),
        status=Status.in_progress,
        date_updated=timezone.now() - timedelta(minutes=16),
    )

    cleanup_artifacts(_process_artifact=mock_process_artifact)

    mock_process_artifact.assert_called_once_with(artifact_id=artifact.id)
    assert artifact.status == Status.queued


def test_cleanup_artifacts_old_file(mocker, db_session):
    mock_process_artifact = mocker.Mock()

    artifact = factories.ArtifactFactory.create(
        job=factories.JobFactory(finished=True),
        status=Status.finished,
        date_created=timezone.now() - timedelta(days=45),
    )

    cleanup_artifacts(_process_artifact=mock_process_artifact)

    assert not mock_process_artifact.mock_calls
    assert artifact.status == Status.expired
    assert not artifact.file
