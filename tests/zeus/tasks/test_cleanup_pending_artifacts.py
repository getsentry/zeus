from datetime import timedelta

from zeus import factories
from zeus.models import PendingArtifact
from zeus.tasks import cleanup_pending_artifacts
from zeus.utils import timezone


def test_cleanup_pending_artifacts_current(mocker, db_session):
    pending_artifact = factories.PendingArtifactFactory.create()

    cleanup_pending_artifacts()

    assert PendingArtifact.query.unrestricted_unsafe().get(pending_artifact.id)


def test_cleanup_pending_artifacts_old_file(mocker, db_session):
    pending_artifact = factories.PendingArtifactFactory.create(
        date_created=timezone.now() - timedelta(days=2)
    )

    cleanup_pending_artifacts()

    assert not PendingArtifact.query.unrestricted_unsafe().get(pending_artifact.id)
