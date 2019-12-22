from datetime import datetime, timedelta

from zeus.tasks import sync_all_repos
from zeus.utils import timezone


def test_sync_all_repos_with_next_update(mocker, db_session, default_repo):
    default_repo.next_update = datetime(2016, 1, 1)
    db_session.add(default_repo)
    db_session.flush()

    mock_sync_repo = mocker.patch("zeus.tasks.sync_repo.delay")

    sync_all_repos()

    mock_sync_repo.assert_called_once_with(repo_id=default_repo.id)


def test_sync_all_repos_with_no_next_update(mocker, db_session, default_repo):
    default_repo.next_update = None
    db_session.add(default_repo)
    db_session.flush()

    mock_sync_repo = mocker.patch("zeus.tasks.sync_repo.delay")

    sync_all_repos()

    mock_sync_repo.assert_called_once_with(repo_id=default_repo.id)


def test_sync_all_repos_with_future_next_update(mocker, db_session, default_repo):
    default_repo.next_update = timezone.now() + timedelta(hours=1)
    db_session.add(default_repo)
    db_session.flush()

    mock_sync_repo = mocker.patch("zeus.tasks.sync_repo.delay")

    sync_all_repos()

    assert not mock_sync_repo.mock_calls
