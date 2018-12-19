from datetime import datetime

from zeus.tasks import sync_all_repos


def test_sync_all_repos(mocker, db_session, default_repo):
    default_repo.last_update_attempt = datetime(2016, 1, 1)
    db_session.add(default_repo)
    db_session.flush()

    mock_sync_repo = mocker.patch("zeus.tasks.sync_repo.delay")

    sync_all_repos()

    mock_sync_repo.assert_called_once_with(repo_id=default_repo.id)
