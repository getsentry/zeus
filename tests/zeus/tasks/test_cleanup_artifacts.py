from datetime import timedelta

from zeus import factories
from zeus.constants import Status
from zeus.tasks import cleanup_artifacts
from zeus.utils import timezone


def test_cleanup_artifacts_current(mocker, db_session):
    artifact = factories.ArtifactFactory.create(status=Status.finished)

    cleanup_artifacts()

    assert artifact.status == Status.finished


def test_cleanup_artifacts_old_file(mocker, db_session):
    artifact = factories.ArtifactFactory.create(
        status=Status.finished, date_created=timezone.now() - timedelta(days=45)
    )

    cleanup_artifacts()

    assert artifact.status == Status.expired
    assert not artifact.file
