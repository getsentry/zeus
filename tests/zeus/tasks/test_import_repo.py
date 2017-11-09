from datetime import datetime

from zeus.tasks import import_repo
from zeus.models import Repository, RepositoryStatus
from zeus.vcs.base import Vcs, RevisionResult


def test_import_repo(mocker, db_session, default_repo):
    mock_vcs_backend = mocker.MagicMock(spec=Vcs)
    mock_get_vcs = mocker.patch.object(
        Repository, 'get_vcs', return_value=mock_vcs_backend)
    mock_delay = mocker.patch.object(import_repo, 'delay')

    def log(parent):
        if parent is None:
            yield RevisionResult(
                sha='a' * 40,
                message='hello world!',
                author='Example <foo@example.com>',
                author_date=datetime(2013, 9, 19, 22, 15, 22),
            )

    mock_vcs_backend.log.side_effect = log

    import_repo(repo_id=default_repo.id)

    mock_get_vcs.assert_called_once_with()
    mock_vcs_backend.log.assert_called_once_with(parent=None)

    assert default_repo.last_update_attempt is not None
    assert default_repo.last_update is not None
    assert default_repo.status == RepositoryStatus.active

    # build sync is abstracted via sync_with_builder
    mock_vcs_backend.update.assert_called_once_with()

    # ensure signal is fired
    mock_delay.assert_called_once_with(
        repo_id=default_repo.id,
        parent='a' * 40,
    )
